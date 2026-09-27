terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project                 = "floci-local"
  region                  = "us-central1"
  access_token            = "fake-token"
  storage_custom_endpoint = "http://localhost:4588/storage/v1/"
}

resource "google_storage_bucket" "bronze" {
  name          = "bank-medallion-bronze"
  location      = "US"
  force_destroy = true
}

resource "google_storage_bucket" "silver" {
  name          = "bank-medallion-silver"
  location      = "US"
  force_destroy = true
}

resource "google_storage_bucket" "gold" {
  name          = "bank-medallion-gold"
  location      = "US"
  force_destroy = true
}