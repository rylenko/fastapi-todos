-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
	"id" SERIAL NOT NULL PRIMARY KEY,
	"created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
	"updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
	"phone_number" VARCHAR(17) NOT NULL UNIQUE,
	"password" VARCHAR(255) NOT NULL,
	"is_active" BOOL NOT NULL  DEFAULT True,
	"phone_number_is_confirmed" BOOL NOT NULL  DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_user_phone_n_c3c403" ON "user" ("phone_number");
CREATE TABLE IF NOT EXISTS "todo" (
	"id" SERIAL NOT NULL PRIMARY KEY,
	"created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
	"updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
	"image_filename" VARCHAR(40),
	"title" VARCHAR(140) NOT NULL,
	"text" TEXT NOT NULL,
	"owner_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_todo_title_43b9b5" ON "todo" ("title");
CREATE TABLE IF NOT EXISTS "aerich" (
	"id" SERIAL NOT NULL PRIMARY KEY,
	"version" VARCHAR(255) NOT NULL,
	"app" VARCHAR(20) NOT NULL,
	"content" JSONB NOT NULL
);
