package com.github.tomakehurst.crashtest;


import com.github.tomakehurst.wiremock.client.WireMock;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.util.EntityUtils;

import javax.ws.rs.GET;
import javax.ws.rs.Path;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;

import static com.github.tomakehurst.wiremock.client.WireMock.*;

@Path("/")
public class CrashTestResource {

    private final HttpClient httpClient;
    private final String wireMockHost;

    public CrashTestResource(HttpClient httpClient, String wireMockHost, WireMock wireMock) {
        this.httpClient = httpClient;
        this.wireMockHost = wireMockHost;

        wireMock.resetMappings();
        wireMock.register(get(urlEqualTo("/something")).willReturn(aResponse().withStatus(200).withBody("Success")));
    }

    @GET
    public String root() {
        return "Uh-oh...";
    }

    @GET
    @Path("http-client-1")
    public String httpClientWithBadErrorHandling() {
        HttpGet get = new HttpGet("http://" + wireMockHost + ":8080/something");
        HttpResponse response;
        try {
            response = httpClient.execute(get);
            String result = EntityUtils.toString(response.getEntity());
            get.releaseConnection();
            return result;
        } catch (IOException ioe) {

            StringWriter stringWriter = new StringWriter();
            PrintWriter pw = new PrintWriter(stringWriter);
            ioe.printStackTrace(pw);
            return "Failure:\n" + stringWriter.toString();
        }
    }

}
