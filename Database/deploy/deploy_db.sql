drop table if exists raw;
drop table if exists metrics;

create table if not exists raw
(
    account_id           bigint,
    "name"               text,
    point                text,
    call_count           bigint,
    total_call_time      bigint,
    total_exclusive_time bigint,
    min_call_time        bigint,
    max_call_time        bigint,
    sum_of_squares       bigint,
    instances            bigint,
    language             text,
    app_name             text,
    app_id               numeric,
    "scope"              text,
    host                 text,
    display_host         text,
    pid                  bigint,
    agent_version        text,
    labels               text
);

create table if not exists metrics
(
    "time"          text,
    web_response    bigint,
    throughput      bigint,
    apdex           bigint,
    error_rate      bigint
);
