-- Enable RLS on user-owned tables
alter table users enable row level security;
alter table profiles enable row level security;
alter table goals enable row level security;
alter table custom_foods enable row level security;
alter table meals enable row level security;
alter table meal_items enable row level security;
alter table recipes enable row level security;
alter table recipe_items enable row level security;
alter table daily_nutrition enable row level security;
alter table body_measurements enable row level security;
alter table progress_photos enable row level security;
alter table step_logs enable row level security;
alter table sleep_logs enable row level security;
alter table recovery_logs enable row level security;
alter table pain_logs enable row level security;
alter table workout_programs enable row level security;
alter table workout_days enable row level security;
alter table workouts enable row level security;
alter table workout_exercises enable row level security;
alter table workout_sets enable row level security;
alter table ai_conversations enable row level security;
alter table ai_messages enable row level security;
alter table ai_daily_reports enable row level security;
alter table ai_weekly_reports enable row level security;

-- owner policies (example for directly user-owned tables)
create policy users_owner on users for all using (id = auth.uid()) with check (id = auth.uid());
create policy profiles_owner on profiles for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy goals_owner on goals for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy custom_foods_owner on custom_foods for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy meals_owner on meals for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy recipes_owner on recipes for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy daily_nutrition_owner on daily_nutrition for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy body_measurements_owner on body_measurements for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy progress_photos_owner on progress_photos for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy step_logs_owner on step_logs for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy sleep_logs_owner on sleep_logs for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy recovery_logs_owner on recovery_logs for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy workout_programs_owner on workout_programs for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy workouts_owner on workouts for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy ai_conversations_owner on ai_conversations for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy ai_daily_reports_owner on ai_daily_reports for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy ai_weekly_reports_owner on ai_weekly_reports for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- child table policies through joins
create policy meal_items_owner on meal_items for all
using (exists (select 1 from meals m where m.id = meal_items.meal_id and m.user_id = auth.uid()))
with check (exists (select 1 from meals m where m.id = meal_items.meal_id and m.user_id = auth.uid()));

create policy recipe_items_owner on recipe_items for all
using (exists (select 1 from recipes r where r.id = recipe_items.recipe_id and r.user_id = auth.uid()))
with check (exists (select 1 from recipes r where r.id = recipe_items.recipe_id and r.user_id = auth.uid()));

create policy pain_logs_owner on pain_logs for all
using (exists (select 1 from recovery_logs r where r.id = pain_logs.recovery_log_id and r.user_id = auth.uid()))
with check (exists (select 1 from recovery_logs r where r.id = pain_logs.recovery_log_id and r.user_id = auth.uid()));

create policy workout_days_owner on workout_days for all
using (exists (select 1 from workout_programs p where p.id = workout_days.program_id and p.user_id = auth.uid()))
with check (exists (select 1 from workout_programs p where p.id = workout_days.program_id and p.user_id = auth.uid()));

create policy workout_exercises_owner on workout_exercises for all
using (exists (select 1 from workouts w where w.id = workout_exercises.workout_id and w.user_id = auth.uid()))
with check (exists (select 1 from workouts w where w.id = workout_exercises.workout_id and w.user_id = auth.uid()));

create policy workout_sets_owner on workout_sets for all
using (
  exists (
    select 1 from workout_exercises we
    join workouts w on w.id = we.workout_id
    where we.id = workout_sets.workout_exercise_id and w.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from workout_exercises we
    join workouts w on w.id = we.workout_id
    where we.id = workout_sets.workout_exercise_id and w.user_id = auth.uid()
  )
);

create policy ai_messages_owner on ai_messages for all
using (exists (select 1 from ai_conversations c where c.id = ai_messages.conversation_id and c.user_id = auth.uid()))
with check (exists (select 1 from ai_conversations c where c.id = ai_messages.conversation_id and c.user_id = auth.uid()));
