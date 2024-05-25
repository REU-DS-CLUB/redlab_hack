drop table if exists metrics;

create table if not exists metrics
(
    "time"          text,
    time_numeric    text,
    web_response    text,
    throughput      text,
    apdex           text,
    error_rate      text
);
