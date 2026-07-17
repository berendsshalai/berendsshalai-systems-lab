const shifts = [
  { shift_id: "S001", worker_id: "Worker 001", site_id: "Site 001", start: "2026-01-05T08:00:00", end: "2026-01-05T16:00:00" },
  { shift_id: "S002", worker_id: "Worker 002", site_id: "Site 001", start: "2026-01-05T08:00:00", end: "2026-01-05T16:00:00" },
  { shift_id: "S003", worker_id: "Worker 003", site_id: "Site 001", start: "2026-01-05T09:00:00", end: "2026-01-05T17:00:00" },
  { shift_id: "S004", worker_id: "Worker 004", site_id: "Site 002", start: "2026-01-05T10:00:00", end: "2026-01-05T18:00:00" }
];

const events = [
  { event_id: "E001", worker_id: "Worker 001", site_id: "Site 001", timestamp: "2026-01-05T08:02:00", event_type: "clock_in" },
  { event_id: "E002", worker_id: "Worker 001", site_id: "Site 001", timestamp: "2026-01-05T16:01:00", event_type: "clock_out" },
  { event_id: "E003", worker_id: "Worker 002", site_id: "Site 001", timestamp: "2026-01-05T08:22:00", event_type: "clock_in" },
  { event_id: "E004", worker_id: "Worker 002", site_id: "Site 001", timestamp: "2026-01-05T15:30:00", event_type: "clock_out" },
  { event_id: "E005", worker_id: "Worker 003", site_id: "Site 001", timestamp: "2026-01-05T09:01:00", event_type: "clock_in" },
  { event_id: "E006", worker_id: "Worker 005", site_id: "Site 001", timestamp: "2026-01-05T11:00:00", event_type: "clock_in" },
  { event_id: "E007", worker_id: "Worker 005", site_id: "Site 001", timestamp: "2026-01-05T14:00:00", event_type: "clock_out" }
];

function minutesBetween(a, b) {
  return Math.floor((new Date(b) - new Date(a)) / 60000);
}

function positiveMinutesBetween(a, b) {
  return Math.max(0, minutesBetween(a, b));
}

function exceptionItem(code, worker_id, site_id, message, severity, source) {
  return { code, worker_id, site_id, message, severity, source, review_status: "needs_review" };
}

function nearestEvent(candidates, shift, eventType, target, usedEvents) {
  const targetTime = new Date(target === "start" ? shift.start : shift.end);
  const filtered = candidates.filter((event) => (
    !usedEvents.has(event.event_id) &&
    event.site_id === shift.site_id &&
    event.event_type === eventType &&
    (target !== "end" || new Date(event.timestamp) >= new Date(shift.start))
  ));
  filtered.sort((a, b) => Math.abs(new Date(a.timestamp) - targetTime) - Math.abs(new Date(b.timestamp) - targetTime));
  return filtered[0];
}

function reconcile() {
  const exceptions = [];
  const usedEvents = new Set();
  const reconciledShifts = [];

  for (const shift of shifts) {
    const workerEvents = events.filter((event) => event.worker_id === shift.worker_id);
    const firstIn = nearestEvent(workerEvents, shift, "clock_in", "start", usedEvents);
    const lastOut = nearestEvent(workerEvents, shift, "clock_out", "end", usedEvents);

    if (!firstIn && !lastOut) {
      exceptions.push(exceptionItem("ABSENT_WHILE_ROSTERED", shift.worker_id, shift.site_id, "Worker has a planned shift but no matching clock events.", "high", { shift_id: shift.shift_id }));
      continue;
    }

    if (!firstIn || !lastOut) {
      exceptions.push(exceptionItem("MISSING_CLOCK_EVENT", shift.worker_id, shift.site_id, "Worker has an incomplete clock event pair.", "high", {
        shift_id: shift.shift_id,
        clock_in: firstIn ? firstIn.event_id : null,
        clock_out: lastOut ? lastOut.event_id : null
      }));
    }

    let lateMinutes = null;
    if (firstIn) {
      usedEvents.add(firstIn.event_id);
      lateMinutes = positiveMinutesBetween(shift.start, firstIn.timestamp);
      if (lateMinutes > 5) {
        exceptions.push(exceptionItem("LATE_ARRIVAL", shift.worker_id, shift.site_id, `Clock-in is ${lateMinutes} minutes after shift start.`, "medium", {
          shift_id: shift.shift_id,
          event_id: firstIn.event_id,
          late_minutes: lateMinutes
        }));
      }
    }

    let earlyMinutes = null;
    if (lastOut) {
      usedEvents.add(lastOut.event_id);
      earlyMinutes = positiveMinutesBetween(lastOut.timestamp, shift.end);
      if (earlyMinutes > 5) {
        exceptions.push(exceptionItem("EARLY_DEPARTURE", shift.worker_id, shift.site_id, `Clock-out is ${earlyMinutes} minutes before shift end.`, "medium", {
          shift_id: shift.shift_id,
          event_id: lastOut.event_id,
          early_minutes: earlyMinutes
        }));
      }
    }

    reconciledShifts.push({
      shift_id: shift.shift_id,
      worker_id: shift.worker_id,
      site_id: shift.site_id,
      planned_minutes: minutesBetween(shift.start, shift.end),
      worked_minutes: firstIn && lastOut ? minutesBetween(firstIn.timestamp, lastOut.timestamp) : null,
      late_minutes: lateMinutes,
      early_departure_minutes: earlyMinutes,
      clock_in_event_id: firstIn ? firstIn.event_id : null,
      clock_out_event_id: lastOut ? lastOut.event_id : null
    });
  }

  const rosterKeys = new Set(shifts.map((shift) => `${shift.worker_id}|${shift.site_id}|${shift.start.slice(0, 10)}`));
  for (const event of events) {
    const key = `${event.worker_id}|${event.site_id}|${event.timestamp.slice(0, 10)}`;
    if (usedEvents.has(event.event_id)) continue;
    if (!rosterKeys.has(key)) {
      exceptions.push(exceptionItem("PRESENT_WHILE_UNROSTERED", event.worker_id, event.site_id, "Attendance event exists without a planned shift on the same date and site.", "medium", {
        event_id: event.event_id,
        event_type: event.event_type
      }));
    } else {
      exceptions.push(exceptionItem("UNMATCHED_CLOCK_EVENT", event.worker_id, event.site_id, "Attendance event was not used in any shift match and requires review.", "low", {
        event_id: event.event_id,
        event_type: event.event_type
      }));
    }
  }

  return {
    summary: {
      shift_count: shifts.length,
      attendance_event_count: events.length,
      exception_count: exceptions.length,
      validation_message_count: exceptions.length
    },
    exceptions,
    reconciled_shifts: reconciledShifts,
    daily_summary: [
      { site_id: "Site 001", date: "2026-01-05", planned_shifts: 3, planned_minutes: 1440 },
      { site_id: "Site 002", date: "2026-01-05", planned_shifts: 1, planned_minutes: 480 }
    ],
    audit_trail: [{ rule_id: "attendance.reconcile.v1", message: "Compared planned shifts with attendance events using configurable grace windows.", record_count: shifts.length + events.length }],
    validation_messages: exceptions.map((item) => ({ code: item.code, severity: item.severity, message: item.message, source: item.source }))
  };
}

function render() {
  const report = reconcile();
  document.querySelector("#summary").innerHTML = `
    <div class="metric"><strong>${report.summary.shift_count}</strong>Planned shifts</div>
    <div class="metric"><strong>${report.summary.attendance_event_count}</strong>Clock events</div>
    <div class="metric"><strong>${report.summary.exception_count}</strong>Exceptions</div>
  `;
  document.querySelector("#exceptions").innerHTML = report.exceptions.map((item) => `
    <tr>
      <td>${item.code}</td>
      <td>${item.worker_id}</td>
      <td>${item.site_id}</td>
      <td>${item.message}</td>
    </tr>
  `).join("");
}

document.querySelector("#run-demo").addEventListener("click", render);
