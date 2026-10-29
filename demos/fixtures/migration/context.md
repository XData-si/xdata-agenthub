# Context

- PostgreSQL 16, table `users` with about 40 million rows; column `fullname text not null`.
- A web application (several instances behind a load balancer) reads and writes `users.fullname` on every login.
- Deployments are rolling: old and new application versions run side by side for up to 30 minutes.
- Goal: the column should be called `display_name`.
