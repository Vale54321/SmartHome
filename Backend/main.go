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

	router.GET("/api/consumption", func(c *gin.Context) {
		rangeInHours := c.DefaultQuery("range", "1")
		aggregateInMinutes := c.DefaultQuery("aggregate", "1")
		query := fmt.Sprintf(`from(bucket: "battery-modbus")
			|> range(start: -%sh)
			|> filter(fn: (r) => r["_measurement"] == "battery_modbus_metrics")
			|> filter(fn: (r) => r["_field"] == "value_watts")
			|> filter(fn: (r) => r["metric"] == "house_consumption")
			|> aggregateWindow(every: %sm, fn: mean, createEmpty: false)
			|> yield(name: "mean")`, rangeInHours, aggregateInMinutes)

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
	})

	// Run server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8085"
	}
	fmt.Println("Serving on http://localhost:" + port)
	router.Run(":" + port)
}
