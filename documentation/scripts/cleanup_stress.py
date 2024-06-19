import os
import time


class cleanup():
    def __init__(self) -> None:
        self.cleanup_run()

    def cleanup_run(self):
        self.cleanup_pcaps()
        self.cleanup_logs()

    def cleanup_pcaps(self):
        path = "/pcaps"
        files = os.listdir(path)
        print(files)
        for file in files:
            file_path = os.path.join(path, file)
            os.remove(file_path)

    def cleanup_logs(self):
        path = "/services/sceam/instance/service.log"
        if os.path.exists(path):
            print("deted logs")
            os.remove(path)


if __name__ == '__main__':
    seconds_to_sleep = 60*5
    while True:
        print(f"Running cleanup every {seconds_to_sleep} seconds")
        cleanup()
        time.sleep(seconds_to_sleep)
