package com.github.tomakehurst.crashtest;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.yammer.dropwizard.config.Configuration;

public class CrashTestConfig extends Configuration {

    @JsonProperty
    private String dummy = "whatever";
}
