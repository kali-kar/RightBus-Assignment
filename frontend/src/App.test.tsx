import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";

const bus = { trip_id: "T1", operator: "Op One", bus_type: "AC Sleeper", bus_seat_type: "Sleeper", is_ac: true, amenities: [],
  from_city_name: "Bangalore", to_city_name: "Mumbai",
  schedule: { departure_time: "4:00 PM", arrival_time: "11:00 AM", departure_date: "2026-08-09", estimated_arrival_date: "2026-08-10", duration_minutes: 1140 },
  pricing: { base_fare: 2426, service_tax: 0, surcharges: 0, total_fare: 2426 }, availability: { seats_available: 16 },
  boarding_points: [], dropping_points: [] };
const mockFetch = (buses: unknown[]) => vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ count: buses.length, buses }) }));

test("successful search shows bus cards", async () => {
  mockFetch([bus]); render(<App />);
  fireEvent.click(screen.getByRole("button", { name: /search buses/i }));
  expect(await screen.findByText("Op One")).toBeInTheDocument();
});

test("no results shows empty state", async () => {
  mockFetch([]); render(<App />);
  fireEvent.click(screen.getByRole("button", { name: /search buses/i }));
  await waitFor(() => expect(screen.getByText("No buses found")).toBeInTheDocument());
});
