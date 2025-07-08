package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("Error loading .env file, relying on environment variables")
	}

	token := os.Getenv("INFLUXDB_TOKEN")
	org := os.Getenv("INFLUXDB_ORG")
	url := os.Getenv("INFLUXDB_HOST")

	if token == "" || org == "" || url == "" {
		log.Fatal("Missing INFLUXDB config")
	}

	client := influxdb2.NewClient(url, token)
	defer client.Close()
	queryAPI := client.QueryAPI(org)

	router := gin.Default()
	router.Use(cors.Default())

	api := router.Group("/api")
	{
		// value_watts
		dataType := "value_watts"
		api.GET("/additional_feed_in_power", createMetricHandler("additional_feed_in_power", dataType, queryAPI))
		api.GET("/battery_power", createMetricHandler("battery_power", dataType, queryAPI))
		api.GET("/grid_power", createMetricHandler("grid_power", dataType, queryAPI))
		api.GET("/house_consumption", createMetricHandler("house_consumption", dataType, queryAPI))
		api.GET("/pv_power", createMetricHandler("pv_power", dataType, queryAPI))
		api.GET("/wallbox_consumption", createMetricHandler("wallbox_consumption", dataType, queryAPI))
		api.GET("/wallbox_solar_consumption", createMetricHandler("wallbox_solar_consumption", dataType, queryAPI))

		// value_percent
		dataType = "value_percent"
		api.GET("/battery_soc", createMetricHandler("battery_soc", dataType, queryAPI))
		api.GET("/self_consumption", createMetricHandler("self_consumption", dataType, queryAPI))
		api.GET("/self_sufficiency", createMetricHandler("self_sufficiency", dataType, queryAPI))

		api.GET("/now", func(c *gin.Context) {
			query := `from(bucket: "battery-modbus")
				|> range(start: -15m)
				|> filter(fn: (r) => r["_measurement"] == "battery_modbus_metrics")
				|> filter(fn: (r) => r["_field"] == "value_watts" or r["_field"] == "value_percent")
				|> last()`

			result, err := queryAPI.Query(context.Background(), query)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}

			data := gin.H{}
			for result.Next() {
				record := result.Record()
				metric := record.ValueByKey("metric")
				if metric != nil {
					data[metric.(string)] = record.Value()
				}
			}

			if err := result.Err(); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}

			c.JSON(http.StatusOK, data)
		})
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8085"
	}
	fmt.Println("Serving on http://localhost:" + port)
	router.Run(":" + port)
}

func createMetricHandler(metricName string, dataType string, queryAPI api.QueryAPI) gin.HandlerFunc {
	return func(c *gin.Context) {
		rangeInHours := c.DefaultQuery("range", "1")
		aggregateInMinutes := c.DefaultQuery("aggregate", "1")
		query := fmt.Sprintf(`from(bucket: "battery-modbus")
			|> range(start: -%sh)
			|> filter(fn: (r) => r["_measurement"] == "battery_modbus_metrics")
			|> filter(fn: (r) => r["_field"] == "%s")
			|> filter(fn: (r) => r["metric"] == "%s")
			|> aggregateWindow(every: %sm, fn: mean, createEmpty: false)
			|> yield(name: "mean")`, rangeInHours, dataType, metricName, aggregateInMinutes)

		result, err := queryAPI.Query(context.Background(), query)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		points := []gin.H{}
		for result.Next() {
			points = append(points, gin.H{
				"time":  result.Record().Time().Format(time.RFC3339),
				"value": result.Record().Value(),
			})
		}

		if err := result.Err(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, points)
	}
}
