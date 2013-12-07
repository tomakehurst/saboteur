package com.github.tomakehurst.crashtest;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.github.tomakehurst.wiremock.WireMockServer;
import com.github.tomakehurst.wiremock.client.WireMock;
import com.yammer.dropwizard.client.HttpClientBuilder;
import com.yammer.dropwizard.client.HttpClientConfiguration;
import com.yammer.dropwizard.config.Configuration;
import org.apache.http.client.HttpClient;

import javax.validation.constraints.NotNull;

public class CrashTestConfig extends Configuration {

    @JsonProperty
    @NotNull
    private String wireMockHost;

    @JsonProperty
    private HttpClientConfiguration clientConfig = new HttpClientConfiguration();

    public String getWireMockHost() {
        return wireMockHost;
    }

    public HttpClient createHttpClient() {
        return new HttpClientBuilder().using(clientConfig).build();
    }

    public WireMock createWireMockClient() {
        return new WireMock(wireMockHost, 8080);
    }

}
