# Orders API — Access Rules

- AC-1: Every endpoint requires a valid bearer token; missing or unknown tokens return 401.
- AC-2: `GET /orders/{id}` returns 200 with the order to its owner or to an admin.
- AC-3: Any other authenticated user requesting someone else's order receives 403. The response must not reveal whether the order exists.
- AC-4: Unknown order ids return 404 to admins. Non-admin users receive 403 for any order they do not own, whether or not it exists, so existence is never leaked.
- AC-5: `DELETE /orders/{id}` is allowed only for admins (204); everyone else receives 403.
