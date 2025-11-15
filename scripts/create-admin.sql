-- Script to create default admin user
-- Run this after database initialization

-- Insert default admin user
-- Email: admin@vietcms.com
-- Password: admin123 (change this in production!)
INSERT INTO admins (email, password_hash, name, role, is_active, created_at)
VALUES ('admin@vietcms.com', 'admin123', 'System Administrator', 'admin', true, now())
ON CONFLICT (email) DO NOTHING;

-- You can add more admin users here if needed
-- Remember to use proper password hashing in production!

