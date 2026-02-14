-- Index Optimizations for db-8 Job Market Intelligence Database
-- Generated from query performance optimizer report
-- Report Date: 20260204-1909
-- 
-- These indexes are recommended based on query pattern analysis of all 30 queries.
-- All indexes are high-priority recommendations for optimal query performance.
--
-- Apply this script AFTER data has been loaded for best performance.
-- Index creation may take time on large tables.

-- ============================================================================
-- HIGH PRIORITY INDEXES
-- ============================================================================

-- 1. Composite index for job_postings with date, location, and active filter
--    Optimizes queries filtering by posted_date, location_state, and is_active
--    Partial index (WHERE is_active = TRUE) reduces index size
CREATE INDEX IF NOT EXISTS idx_job_postings_date_location_active 
ON job_postings(posted_date DESC, location_state, is_active) 
WHERE is_active = TRUE;

-- 2. Composite index for user_skills table
--    Optimizes queries joining user_skills with skills and job_skills_requirements
--    Common pattern: matching user skills to job requirements
CREATE INDEX IF NOT EXISTS idx_user_skills_user_skill 
ON user_skills(user_id, skill_id);

-- 3. Composite index for job_skills_requirements table
--    Optimizes queries filtering by job_id and requirement_type
--    Common pattern: finding required vs preferred skills for jobs
CREATE INDEX IF NOT EXISTS idx_job_skills_req_job_type 
ON job_skills_requirements(job_id, requirement_type);

-- ============================================================================
-- INDEX CREATION NOTES
-- ============================================================================
--
-- After creating indexes, analyze tables to update statistics:
--   ANALYZE job_postings;
--   ANALYZE user_skills;
--   ANALYZE job_skills_requirements;
--
-- Monitor index usage:
--   SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
--   FROM pg_stat_user_indexes
--   WHERE schemaname = 'public'
--   ORDER BY tablename, indexname;
--
-- If indexes are not being used, consider dropping them to save space:
--   DROP INDEX IF EXISTS idx_name;
