# Kubernetes Twitter scraper
Built with tweepy to listen to twitters streaming api for a geo fenced area, optionally only record tags with actual lat/long values

# TLDR
```console
$ helm repo add twitsss https://ssaraswati.github.io/Twitsss
$ helm install twitsss/twitsss
```

## Introduction

This chart bootstraps an Twitter scraper deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites
  - Kubernetes 1.8+

## Installing the Chart

To install the chart with the release name `my-release`:

```console
$ helm repo add twitsss https://ssaraswati.github.io/Twitsss
$ helm install twitsss/twitsss
```

The command deploys Twitsss on the Kubernetes cluster in the default configuration. The [configuration](#configuration) section lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```console
$ helm delete my-release
```
The command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

The following table lists the configurable parameters of the Twitsss chart and their default values.

Parameter | Description | Default
--- | --- | ---
`scraper.image.repository` | container image repository | `twitsss`
`scraper.image.tag` | container image tag | `latest`
`scraper.image.pullPolicy` | container image pull policy | `Always`
`scrapers.[0].description` | name what area you are scraping | `melbourne`
`scrapers.[0].boundingBox` | lat long bounding box to listen to | `144.5,-38.1,145.5,-37.5`
`scrapers.[0].bufferSize` | how many tweets to save in memory before writing to disk | `100`
`scrapers.[0].geoOnly` | filter saved tweets to only those with lat long | `true`
`scrapers.[0].twitterConsumerKey` | twitter ConsumerKey |  _empty_
`scrapers.[0].twitterConsumerSecret` | twitter ConsumerSecret |  _empty_
`scrapers.[0].twitterAccessKey` | twitter AccessKey |  _empty_
`scrapers.[0].twitterAccessSecret` | twitter AccessSecret |  _empty_
`persistence.enabled` | Enables persistent volume - PV provisioner support necessary | true
`persistence.accessMode` | PVC Access Mode | ReadWriteMany
`persistence.size` | PVC Size | 8Gi
`persistence.storageClass` | PVC Storage Class | _empty_
`persistence.mountPath` | PVC Storage Class | /twitter

