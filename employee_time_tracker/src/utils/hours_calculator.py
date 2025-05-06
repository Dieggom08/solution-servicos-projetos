
from datetime import datetime, timedelta, time
from collections import defaultdict

# Constants (can be made configurable later)
WEEKLY_HOURS_TARGET = 44
DAILY_HOURS_TARGET = 8
SATURDAY_HOURS_TARGET = 4
NIGHT_SHIFT_START = time(22, 0, 0)
NIGHT_SHIFT_END = time(5, 0, 0)

def calculate_worked_hours(records):
    """
    Calculates worked hours, overtime, and night shift hours from time records.

    Args:
        records (list): A list of TimeRecord objects for a specific period, ordered by timestamp.

    Returns:
        dict: A dictionary containing weekly summaries with total worked seconds,
              approximate overtime seconds, and night shift seconds.
              Example: {
                  'YYYY-WW': { # Year and Week number
                      'week_start': 'YYYY-MM-DD',
                      'week_end': 'YYYY-MM-DD',
                      'total_worked_seconds': float,
                      'total_overtime_seconds': float,
                      'total_night_shift_seconds': float
                  }
              }
    """
    weekly_summary = defaultdict(lambda: {
        'total_worked_seconds': 0.0,
        'total_overtime_seconds': 0.0,
        'total_night_shift_seconds': 0.0,
        'days_worked': set()
    })
    pair_start = None

    for record in records:
        record_time = record.timestamp
        record_date = record_time.date()
        week_key = f"{record_date.year}-{record_date.isocalendar()[1]:02d}"

        # Set week start/end dates (simplistic, assumes records are sorted)
        if 'week_start' not in weekly_summary[week_key]:
            start_of_week = record_date - timedelta(days=record_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            weekly_summary[week_key]['week_start'] = start_of_week.strftime('%Y-%m-%d')
            weekly_summary[week_key]['week_end'] = end_of_week.strftime('%Y-%m-%d')

        if record.record_type in ["arrival", "lunch_end"] and pair_start is None:
            pair_start = record_time
        elif record.record_type in ["departure", "lunch_start"] and pair_start is not None:
            duration = record_time - pair_start
            worked_seconds = duration.total_seconds()

            if worked_seconds > 0:
                weekly_summary[week_key]['total_worked_seconds'] += worked_seconds
                weekly_summary[week_key]['days_worked'].add(record_date)

                # Calculate night shift hours within this interval
                current_time = pair_start
                while current_time < record_time:
                    next_time = current_time + timedelta(minutes=1)
                    # Check if the *middle* of the minute interval falls within night shift
                    check_time = (current_time + timedelta(seconds=30)).time()
                    is_night = False
                    if NIGHT_SHIFT_START <= NIGHT_SHIFT_END: # Shift doesn't cross midnight
                        if NIGHT_SHIFT_START <= check_time < NIGHT_SHIFT_END:
                            is_night = True
                    else: # Shift crosses midnight
                        if check_time >= NIGHT_SHIFT_START or check_time < NIGHT_SHIFT_END:
                            is_night = True

                    if is_night:
                        weekly_summary[week_key]['total_night_shift_seconds'] += min(60, (record_time - current_time).total_seconds())

                    current_time = next_time

            pair_start = None # Reset for the next pair

    # Calculate approximate overtime (simple weekly target comparison)
    for week_key, summary in weekly_summary.items():
        target_seconds = WEEKLY_HOURS_TARGET * 3600
        if summary['total_worked_seconds'] > target_seconds:
            summary['total_overtime_seconds'] = summary['total_worked_seconds'] - target_seconds

    # Convert back to a list format for the report template
    report_list = [
        {**summary, 'week_key': key}
        for key, summary in sorted(weekly_summary.items())
    ]

    return report_list

def determine_absences(start_date, end_date, employees, records):
    """
    Determines potential absence days for employees within a date range.
    An absence is defined as a weekday (Mon-Fri) or Saturday where no time record exists
    for an active employee, considering their admission date.

    Args:
        start_date (date): The start date of the period.
        end_date (date): The end date of the period.
        employees (list): List of active Employee objects.
        records (list): List of TimeRecord objects for the period.

    Returns:
        list: A list of dictionaries, each representing an absence.
              Example: [{'employee_name': str, 'absence_date': 'YYYY-MM-DD', 'justification': str or None}]
    """
    absences = []
    records_by_employee_date = defaultdict(list)
    for r in records:
        records_by_employee_date[(r.employee_id, r.timestamp.date())].append(r)

    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday() # Monday is 0, Sunday is 6

        # Check only workdays (Mon-Sat)
        if day_of_week < 6: # 0-5 are Mon-Sat
            for emp in employees:
                # Check if employee was active on this date
                if emp.status == 'active' and (emp.admission_date is None or emp.admission_date <= current_date):
                    # Check if there are any records for this employee on this date
                    if not records_by_employee_date[(emp.id, current_date)]:
                        absences.append({
                            'employee_name': emp.name,
                            'absence_date': current_date.strftime('%Y-%m-%d'),
                            'justification': None # Placeholder - justification needs separate mechanism
                        })
        current_date += timedelta(days=1)

    return absences

