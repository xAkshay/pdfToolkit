import wx
import PyPDF2
import os

class PDFPasswordProtector(wx.Frame):
    def __init__(self, parent, title):
        super(PDFPasswordProtector, self).__init__(parent, title=title, size=(400, 250))

        self.panel = wx.Panel(self)
        self.create_widgets()

        self.Centre()
        self.Show()

    def create_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # PDF file input
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        pdf_label = wx.StaticText(self.panel, label='Select PDF file:')
        hbox1.Add(pdf_label, flag=wx.RIGHT, border=8)
        self.pdf_path_textctrl = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        hbox1.Add(self.pdf_path_textctrl, proportion=1)
        pdf_button = wx.Button(self.panel, label='Browse', size=(70, 30))
        pdf_button.Bind(wx.EVT_BUTTON, self.on_browse)
        hbox1.Add(pdf_button, flag=wx.LEFT, border=10)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Password input for protection
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        new_password_label = wx.StaticText(self.panel, label='New Password:')
        hbox2.Add(new_password_label, flag=wx.RIGHT, border=8)
        self.new_password_textctrl = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        hbox2.Add(self.new_password_textctrl, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # Protect PDF button
        protect_button = wx.Button(self.panel, label='Protect PDF', size=(150, 30))
        protect_button.Bind(wx.EVT_BUTTON, self.protect_pdf)
        vbox.Add(protect_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        # Separator line
        vbox.Add(wx.StaticLine(self.panel, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), flag=wx.EXPAND | wx.ALL, border=10)

        # Old Password input for removal
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        old_password_label = wx.StaticText(self.panel, label='Old Password:')
        hbox3.Add(old_password_label, flag=wx.RIGHT, border=8)
        self.old_password_textctrl = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        hbox3.Add(self.old_password_textctrl, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # Remove Password button
        remove_password_button = wx.Button(self.panel, label='Remove Password', size=(150, 30))
        remove_password_button.Bind(wx.EVT_BUTTON, self.remove_password)
        vbox.Add(remove_password_button, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        self.panel.SetSizer(vbox)

    def on_browse(self, event):
        file_dialog = wx.FileDialog(self, 'Choose a PDF file', wildcard='PDF files (*.pdf)|*.pdf',
                                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if file_dialog.ShowModal() == wx.ID_OK:
            pdf_path = file_dialog.GetPath()
            self.pdf_path_textctrl.SetValue(pdf_path)
        file_dialog.Destroy()

    def protect_pdf(self, event):
        pdf_path = self.pdf_path_textctrl.GetValue()
        new_password = self.new_password_textctrl.GetValue()

        if not pdf_path or not new_password:
            wx.MessageBox('Please select a PDF file and set a new password.', 'Error', wx.OK | wx.ICON_ERROR)
            return

        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer = PyPDF2.PdfWriter()

                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                pdf_writer.encrypt(new_password)

                output_pdf_path = os.path.splitext(pdf_path)[0] + '_protected.pdf'

                with open(output_pdf_path, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)

                wx.MessageBox(f'PDF successfully protected.\nProtected PDF saved to:\n{output_pdf_path}',
                              'Success', wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            wx.MessageBox(f'Error protecting PDF: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)

    def remove_password(self, event):
        pdf_path = self.pdf_path_textctrl.GetValue()
        old_password = self.old_password_textctrl.GetValue()

        if not pdf_path:
            wx.MessageBox('Please select a PDF file.', 'Error', wx.OK | wx.ICON_ERROR)
            return

        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                if pdf_reader.is_encrypted:
                    if not old_password:
                        wx.MessageBox('Please provide the old password to remove encryption.', 'Error',
                                      wx.OK | wx.ICON_ERROR)
                        return

                    if not pdf_reader.decrypt(old_password):
                        wx.MessageBox('Old password provided is incorrect.', 'Error', wx.OK | wx.ICON_ERROR)
                        return

                    pdf_writer = PyPDF2.PdfWriter()

                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    output_pdf_path = os.path.splitext(pdf_path)[0] + '_unprotected.pdf'

                    with open(output_pdf_path, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)

                    wx.MessageBox(f'Password successfully removed.\nUnprotected PDF saved to:\n{output_pdf_path}',
                                  'Success', wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox('The selected PDF is not password protected.', 'Info', wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            wx.MessageBox(f'Error removing password: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)

if __name__ == '__main__':
    app = wx.App(False)
    frame = PDFPasswordProtector(None, 'PDF Password Protector')
    app.MainLoop()
