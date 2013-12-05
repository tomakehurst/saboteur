package com.github.tomakehurst.crashtest;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.yammer.dropwizard.config.Configuration;

import javax.validation.constraints.NotNull;

public class CrashTestConfig extends Configuration {

    @JsonProperty
    @NotNull
    private String wireMockHost;

    public String getWireMockHost() {
        return wireMockHost;
    }
}
