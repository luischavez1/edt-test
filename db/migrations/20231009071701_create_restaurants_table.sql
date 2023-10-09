-- migrate:up
CREATE TABLE "restaurant"
(
    id varchar PRIMARY KEY,
    rating integer,
    "name" varchar,
    site varchar,
    email varchar,
    phone varchar,
    street varchar,
    city varchar,
    "state" varchar,
    lat float,
    lng float,
    location geometry(Point, 4326)
);

-- migrate:down

DROP TABLE "restaurant"

