# Database Cleanup Scripts

## cleanup_users.py

Removes all users from the database except the specified one.

### Usage

**⚠️ WARNING: This script permanently deletes users and all their data. Use with extreme caution!**

#### Local Development:
```bash
cd backend
python -m scripts.cleanup_users
```

#### Production (Render):
1. Connect to your Render service via SSH or use Render Shell
2. Navigate to the backend directory
3. Run:
```bash
python -m scripts.cleanup_users
```

#### Options:
- `--keep-email`: Email of user to keep (default: `alhassane.samassekou@gmail.com`)
- `--yes`: Skip confirmation prompt (use with caution!)

### What Gets Deleted

When a user is deleted, the following related data is also removed:
- All analyses (cascade delete)
- Admin logs
- Job matches
- Interview prep records
- Company intelligence records
- Career path records
- User skill history
- User role associations

The following data is preserved but updated:
- Guest analyses: `converted_user_id` set to NULL
- System configurations: `updated_by_id` set to NULL
- Keywords: `updated_by_id` set to NULL

### Safety Features

1. **Confirmation Required**: The script requires typing 'DELETE' to confirm
2. **Preview First**: Shows all users and related data counts before deletion
3. **Transaction Safety**: Uses database transactions with rollback on error
4. **Verification**: Shows remaining users after cleanup

### Example Output

```
Found user to keep: alhassane.samassekou@gmail.com (ID: 1)

Found 5 users to delete:
  - user1@example.com (ID: 2)
  - user2@example.com (ID: 3)
  ...

Related data to be deleted:
  - Analyses: 15
  - Admin Logs: 2
  - Job Matches: 8
  ...

⚠️  WARNING: This will permanently delete 5 users and all their data!
Type 'DELETE' to confirm: DELETE

Deleting related data...
✓ Related data deleted

Deleting users...
✓ Deleted 5 users

✓ Cleanup complete! Remaining users: 1
  - alhassane.samassekou@gmail.com (ID: 1)
```

