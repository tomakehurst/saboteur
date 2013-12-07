package com.github.tomakehurst.crashtest;

import com.yammer.dropwizard.Service;
import com.yammer.dropwizard.config.Bootstrap;
import com.yammer.dropwizard.config.Environment;
import com.yammer.metrics.reporting.CsvReporter;

import java.io.File;

import static java.util.concurrent.TimeUnit.SECONDS;

public class CrashTestService extends Service<CrashTestConfig> {

    @Override
    public void initialize(Bootstrap<CrashTestConfig> bootstrap) {
    }

    @Override
    public void run(CrashTestConfig configuration, Environment environment) throws Exception {
//        CsvReporter.enable(new File("/var/log/crash-test-metrics.csv"), 10, SECONDS);
        environment.addResource(new CrashTestResource(
                configuration.createHttpClient(),
                configuration.getWireMockHost(),
                configuration.createWireMockClient()));
    }

    public static void main(String... args) throws Exception {
        if (args.length == 0) {
            new CrashTestService().run(new String[] { "server", "src/main/resources/crash-test.yaml" });
        } else {
            new CrashTestService().run(args);
        }

    }
}
