# Kubernetes Twitter scraper
Built with tweepy to listen to twitters streaming api for a geo fenced area, optionally only record tags with actual lat/long values

## Install with helm
```
docker build -t twitsss .
helm upgrade --install scraper helm
```

## Configuration
credentials and scraping area configured via values file
