package main

import (
	"context"
	"fmt"
	"log"
	"os"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	token := os.Getenv("INFLUXDB_TOKEN")
	org := os.Getenv("INFLUXDB_ORG")
	url := os.Getenv("INFLUXDB_HOST")
	client := influxdb2.NewClient(url, token)

	queryAPI := client.QueryAPI(org)
	query := `from(bucket: "battery-modbus")
                |> range(start: -10m)
                |> filter(fn: (r) => r["_measurement"] == "battery_modbus_metrics")
                |> filter(fn: (r) => r["_field"] == "value_watts")
                |> filter(fn: (r) => r["metric"] == "house_consumption")
                |> yield(name: "filtered")`

	results, err := queryAPI.Query(context.Background(), query)
	if err != nil {
		log.Fatal(err)
	}
	for results.Next() {
		fmt.Println(results.Record())
	}
	if err := results.Err(); err != nil {
		log.Fatal(err)
	}
}
