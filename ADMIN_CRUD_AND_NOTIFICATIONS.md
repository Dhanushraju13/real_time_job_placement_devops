# Admin CRUD and registration notification fixes

## Admin dashboard CRUD
- The administrator's platform-wide job table requests all job statuses, including pending approval and closed jobs.
- The backend restricts `status=ALL` and non-active job listings to authenticated administrators.
- Administrators can delete any job from the dedicated `/api/admin/jobs/{job_id}` endpoint. Deletion failures return a readable conflict instead of silently succeeding.
- Administrators can delete students, recruiters, and other administrator accounts. The currently signed-in administrator cannot delete their own account.
- Admin UI actions check HTTP responses and show errors rather than reporting success when a request fails.
- Pending jobs cannot be activated from the generic status toggle; they must go through the approval workflow.

## Registration notifications
- Student and recruiter public registration creates a persistent notification for every administrator.
- The notification title distinguishes `New Student Registration` from `New Recruiter Registration` and links to the admin area.
- The notification is committed to PostgreSQL before the registration response is returned. Existing notification polling/WebSocket refresh makes the notification appear in the admin notification feed.

## Rebuild and run
```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 backend
```

Open `http://localhost:8081`. Check the Admin Dashboard > Users and Admin Dashboard > All Platform Gigs tabs. Test registration using a new email address while signed in as an administrator in another browser session.

Note: a complete Docker/browser end-to-end run was not available during this package update. Python source syntax was checked; install frontend dependencies and run `npm run build` (or use the Docker build) to validate the frontend in your environment.
