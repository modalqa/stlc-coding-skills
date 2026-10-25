# Todo Store Requirements

- AC-1: Creating a todo requires a title of 1 to 100 characters (after trimming whitespace); otherwise a ValidationError is raised.
- AC-2: A new todo gets a unique integer id and `completed = False`.
- AC-3: Listing returns todos in creation order.
- AC-4: Updating a todo can change its title (same rules as AC-1) and its completed flag.
- AC-5: Deleting a todo removes it; getting, updating or deleting an unknown id raises NotFoundError.
