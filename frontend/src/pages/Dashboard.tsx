import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getDueItems, getUser } from "../api/client";
import { CURRENT_USER_ID } from "../currentUser";

export function Dashboard() {
  const userQuery = useQuery({
    queryKey: ["user", CURRENT_USER_ID],
    queryFn: () => getUser(CURRENT_USER_ID),
  });

  const dueQuery = useQuery({
    queryKey: ["due", CURRENT_USER_ID],
    queryFn: () => getDueItems(CURRENT_USER_ID),
  });

  if (userQuery.isLoading || dueQuery.isLoading) return <p>Loading...</p>;
  if (userQuery.isError) return <p>Failed to load user: {String(userQuery.error)}</p>;
  if (dueQuery.isError) return <p>Failed to load due items: {String(dueQuery.error)}</p>;

  const dueCount = dueQuery.data?.length ?? 0;

  return (
    <div>
      <h1>Welcome, {userQuery.data?.username}</h1>
      <p>{dueCount} item(s) due for review.</p>
      <Link to="/review">Start review</Link>
    </div>
  );
}
