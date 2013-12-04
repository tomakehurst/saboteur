package com.github.tomakehurst.crashtest;

import javax.ws.rs.GET;
import javax.ws.rs.Path;

@Path("/")
public class CrashTestResource {

    @GET
    public String root() {
        return "Uh-oh...";
    }


}
