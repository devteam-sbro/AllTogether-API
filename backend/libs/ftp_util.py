import cgitb;
import ftplib
import logging
import os
import uuid
from datetime import datetime

from backend import app

cgitb.enable()

class FtpUtil:

    @staticmethod
    def check_exist_folder(folder_path, folder, make_folder):


        """
        Folder 존재여부를 체크하여 없으면 생성
        """

        ftp = ftplib.FTP(app.config['CDN_FTP_IP'], app.config['CDN_FTP_ID'],
                         app.config['CDN_FTP_PW'])
        ftp.cwd(folder_path)

        if folder in ftp.nlst():
            logging.debug("already exist folder.")
        else:
            if make_folder:
                ftp.mkd(folder)

    @staticmethod
    def check_exist_file(file_path, file_name):
        """
        파일 존재여부 체크
        """
        result = False

        try:
            ftp = ftplib.FTP(app.config['CDN_FTP_IP'], app.config['CDN_FTP_ID'],
                             app.config['CDN_FTP_PW'])
            ftp.cwd(file_path)

            for file in ftp.nlst():
                if file == file_name:
                    result = True
                    break


        except ftplib.all_errors as e:
            logging.error(e)

        except Exception as e:
            logging.error(e)

        return result

    @staticmethod
    def upload_single_file(file, filepath):
        """

        """

        extension = file.filename.split(".")[1]
        filename = uuid.uuid4().hex + "." + extension

        yyyymm = datetime.today().strftime("%Y%m")

        original_filename = file.filename

        filedirectory = filepath + "/" + yyyymm;
        if not os.path.exists("upload/tmp/" + filedirectory):
            os.makedirs("upload/tmp/" + filedirectory)

        fullpath = "tmp/" + filepath + "/" + yyyymm + "/" + filename
        logging.debug(fullpath)

        # try:
        #     # connect ftp
        #     ftp = ftplib.FTP(app.config['CDN_FTP_IP'], app.config['CDN_FTP_ID'], app.config['CDN_FTP_PW'])
        #     ftp.cwd(filepath)
        #
        #     # display folder list
        #     Log.debug(ftp.nlst())
        #
        #     # folder check
        #     if yyyymm in ftp.nlst():
        #         pass
        #     else:
        #         # make folder
        #         ftp.mkd(yyyymm)
        #
        #     ftp.cwd(yyyymm)
        #     # upload file
        #     ftp.storbinary('STOR ' + filename, file)
        #
        #     ftp.quit()
        #
        # except Exception as e:
        #     Log.debug(str(e))
        #     raise CommonException(e)

        try:
            if file.filename:
                # strip leading path from file name to avoid
                # directory traversal attacks
                open("upload/" + fullpath, 'wb').write(file.read())
                message = 'The file "' + fullpath + '" was uploaded successfully'
            else:
                message = 'No file was uploaded'

        except Exception as e:
            logging.debug(str(e))
            raise Exception(e)

        return {"file_url": FtpUtil.get_file_url(fullpath), "original_filename": original_filename, "filename": filename}

    @staticmethod
    def upload_text_file(filepath, filename, text_content):
        """
        """

        file = open(app.config['FTP_TEMP_FILE_PATH'] + "/" + filename, 'w')
        file.write(text_content)
        file.close()

        file = open(app.config['FTP_TEMP_FILE_PATH'] + "/" + filename, 'rb')

        fullpath = "https://" + app.config['CDN_PATH'] + filepath + "/" + filename
        logging.debug(fullpath)

        ftp = ftplib.FTP(app.config['CDN_FTP_IP'], app.config['CDN_FTP_ID'],
                         app.config['CDN_FTP_PW'])
        ftp.cwd(filepath)
        ftp.storbinary('STOR ' + filename, file)
        ftp.quit()

        file.close()

        return fullpath

    @staticmethod
    def rename_file(file_path, orgin_file, rename_file):
        """
        """

        try:
            ftp = ftplib.FTP(app.config['CDN_FTP_IP'], app.config['CDN_FTP_ID'],
                             app.config['CDN_FTP_PW'])
            ftp.cwd(file_path)
            ftp.rename(orgin_file, rename_file)

        except ftplib.all_errors as e:
            logging.error(e)

    @staticmethod
    def get_file_url(file_path):
        return app.config['TEST_FILE_SERVER_URL'] + file_path
