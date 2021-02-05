CREATE TABLE public.schedule_types
(
    task_name text COLLATE pg_catalog."default",
    period text COLLATE pg_catalog."default",
    task_type_id bigint NOT NULL,
    CONSTRAINT schedule_types_pkey PRIMARY KEY (task_type_id)
)

CREATE TABLE public.schedule_tasks
(
    task_type_id bigint,
    chat_id bigint,
    CONSTRAINT unique_task_to_chat UNIQUE (task_type_id, chat_id),
    CONSTRAINT "task_type_FK" FOREIGN KEY (task_type_id)
        REFERENCES public.schedule_types (task_type_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

INSERT INTO public.schedule_types(
	task_name, period, task_type_id)
	VALUES ('memes', 'daily 10:30', 0);

INSERT INTO public.schedule_types(
	task_name, period, task_type_id)
	VALUES ('wednesday', 'wednesdays', 1);