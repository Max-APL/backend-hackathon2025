class Settings:
    GOOGLE_SHEET_ID = "18S8UejJZ1mOLtsbrryQsa7d99k4wsLCCaKQuwR9eEAA"
    GID_RESULTS = "2023033319"  # hoja Results
    SCRAPE_GID = "0"

    @property
    def google_sheet_url(self) -> str:
        return (
            f"https://docs.google.com/spreadsheets/d/{self.GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&gid={self.GID_RESULTS}"
        )

settings = Settings()
