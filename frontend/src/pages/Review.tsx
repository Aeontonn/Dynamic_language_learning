import { useQuery } from "@tanstack/react-query";
import { getDueItems } from "../api/client";
import { CURRENT_USER_ID } from "../currentUser";

export function Review() {
  const dueQuery = useQuery({
    queryKey: ["due", CURRENT_USER_ID],
    queryFn: () => getDueItems(CURRENT_USER_ID),
  });

  if (dueQuery.isLoading) return <p>Loading...</p>;
  if (dueQuery.isError) return <p>Failed to load due items: {String(dueQuery.error)}</p>;

  const items = dueQuery.data ?? [];

  if (items.length === 0) return <p>Nothing due right now - come back later.</p>;

  // The interactive quiz UI (answering + immediate feedback) is built in Step 5;
  // this list is just the scaffold's read-only view of what's due.
  return (
    <div>
      <h1>Today's review</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            {item.content_item.text} - {item.content_item.translation}
          </li>
        ))}
      </ul>
    </div>
  );
}
