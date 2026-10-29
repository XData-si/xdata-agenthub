This pull request adds `invoices.py`. The application is multi-tenant: every invoice row has a `tenant_id`, and users
may only see invoices of their own tenant (`current_user.tenant_id`). Pages are numbered from 1.
