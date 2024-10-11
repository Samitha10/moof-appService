import sys


def error_message_detail(error, error_detail: sys, custom_message: str = None):
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename

    error_message = f"""
    ---------------Error Details----------------
    Occur in :  [{file_name}] 
    Line Number : [{exc_tb.tb_lineno}]"""

    if custom_message:
        error_message += f"\n    Custom Message : [{custom_message}]"

    if error:
        error_message += f"\n    Original Error : [{str(error)}]"

    return error_message


class CustomException(Exception):
    def __init__(self, error=None, error_detail: sys = sys, custom_message: str = None):
        super().__init__(error)
        self.error_message = error_message_detail(
            error, error_detail=error_detail, custom_message=custom_message
        )

    def __str__(self):
        return self.error_message


# if __name__ == "__main__":
#     try:
#         a = 10 / 0
#     except Exception as e:
#         raise CustomException(e, sys)
