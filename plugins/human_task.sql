CREATE TABLE public.human_task
(
    task_id text,
    claimant text,
    state text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
)

ALTER TABLE public.human_task OWNER to airflow;
