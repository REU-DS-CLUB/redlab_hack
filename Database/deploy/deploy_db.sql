drop table if exists metrics;
drop table if exists labels;

create table if not exists metrics
(
    "time"          text,
    time_numeric    text,
    web_response    text,
    throughput      text,
    apdex           text,
    error_rate      text
);

create table if not exists labels
(
    "time"              timestamp,
    web_responce_labels integer,
    thoughput_labels    integer,
    apdex_labels        integer,
    error_labels        integer
);
