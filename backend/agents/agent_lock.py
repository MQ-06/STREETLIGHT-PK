processing_reports = set()

def acquire_lock(report_id: int) -> bool:
    if report_id in processing_reports:
        return False
    processing_reports.add(report_id)
    return True


def release_lock(report_id: int):
    processing_reports.discard(report_id)