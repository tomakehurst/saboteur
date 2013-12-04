package com.github.tomakehurst.crashtest;

import com.yammer.dropwizard.Service;
import com.yammer.dropwizard.config.Bootstrap;
import com.yammer.dropwizard.config.Environment;

public class CrashTestService extends Service<CrashTestConfig> {

    @Override
    public void initialize(Bootstrap<CrashTestConfig> bootstrap) {
    }

    @Override
    public void run(CrashTestConfig configuration, Environment environment) throws Exception {
        environment.addResource(new CrashTestResource());
    }

    public static void main(String... args) throws Exception {
        if (args.length == 0) {
            new CrashTestService().run(new String[] { "server", "src/main/resources/crash-test.yaml" });
        } else {
            new CrashTestService().run(args);
        }

    }
}
