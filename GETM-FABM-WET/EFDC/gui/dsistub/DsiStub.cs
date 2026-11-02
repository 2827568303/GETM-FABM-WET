using System;
using System.IO;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

// Stub replacement for DSILIC1.dll's licensing classes.
// Reports "activated / perpetual / fully featured" and logs every access to a file.
namespace Flexnet.WrapperDongle
{
    internal static class Log
    {
        private static readonly object Gate = new object();

        public static void W(string s)
        {
            try
            {
                lock (Gate)
                {
                    File.AppendAllText(@"C:\EFDC84_LIC\dsistub_calls.log",
                        DateTime.Now.ToString("HH:mm:ss.fff") + " " + s + Environment.NewLine);
                }
            }
            catch { }
        }
    }

    public static class Util
    {
        public static T G<T>(T v, [CallerMemberName] string m = "")
        {
            Log.W("get " + m + " -> " + (v == null ? "null" : v.ToString()));
            return v;
        }

        public static void S(object v, [CallerMemberName] string m = "")
        {
            Log.W("set " + m + " = " + (v == null ? "null" : v.ToString()));
        }
    }

    [ComVisible(true)]
    [Guid("6399E2C8-63E4-4F31-823C-D256C17E7A13")]
    [ProgId("Flexnet.WrapperDongle.FlexWrapperDongle")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class FlexWrapperDongle
    {
        public const string F = "EE_MULTI_TRIAL_8_4";

        public FlexWrapperDongle() { Log.W("ctor FlexWrapperDongle"); }

        public bool IsActivated { get { return Util.G(true); } set { Util.S(value); } }
        public bool IsDongle { get { return Util.G(false); } set { Util.S(value); } }
        public bool IsReportUsage { get { return Util.G(false); } set { Util.S(value); } }
        public string FeatureName { get { return Util.G(F); } set { Util.S(value); } }
        public string ProdNameVersion { get { return Util.G("EFDC_Explorer8.4"); } set { Util.S(value); } }
        public string LicType { get { return Util.G("PERPETUAL"); } set { Util.S(value); } }
        public string ActivationID { get { return Util.G("A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47"); } set { Util.S(value); } }
        public string FulfillmentID { get { return Util.G("14AC1ACA-EFD2-4C01-A1DD-4397B7F19715"); } set { Util.S(value); } }
        public string UniqueId { get { return Util.G("FB5BE307-6E85-410A-9265-B9389E71E38D"); } set { Util.S(value); } }
        public string LicenseFile { get { return Util.G(@"C:\Users\Public\DSI\EEMS8.4\license.lic"); } set { Util.S(value); } }
        public string FulfillDate { get { return Util.G("2020-01-01"); } set { Util.S(value); } }
        public string ExpirationDate { get { return Util.G("2030-01-01"); } set { Util.S(value); } }
        public string VersionDate { get { return Util.G("2030-01-01"); } set { Util.S(value); } }
        public string LastDate { get { return Util.G("2030-01-01"); } set { Util.S(value); } }
        public string TotalCopies { get { return Util.G("100"); } set { Util.S(value); } }
        public string RemainingCopies { get { return Util.G("100"); } set { Util.S(value); } }
        public string MachineID { get { return Util.G("DISK_SERIAL_NUM=2db6323c"); } set { Util.S(value); } }
        public string LicenseCode { get { return Util.G("A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47"); } set { Util.S(value); } }
        public string ErrorMessage { get { return Util.G(""); } set { Util.S(value); } }
        public int LastError { get { return Util.G(0); } set { Util.S(value); } }

        public bool CheckLicensing() { Log.W("call CheckLicensing"); return true; }
        public bool CheckLicense() { Log.W("call CheckLicense"); return true; }
        public bool IsLicenseValid() { Log.W("call IsLicenseValid"); return true; }
        public bool ValidateProductFeatures() { Log.W("call ValidateProductFeatures"); return true; }
        public bool ValidateFeatures() { Log.W("call ValidateFeatures"); return true; }
        public bool HasFeature(string name) { Log.W("call HasFeature(" + name + ")"); return true; }
        public bool IsFeatureEnabled(string name) { Log.W("call IsFeatureEnabled(" + name + ")"); return true; }
        public bool Initialize() { Log.W("call Initialize"); return true; }
        public bool ReadLicenseInformation() { Log.W("call ReadLicenseInformation"); return true; }
        public bool GetLicense() { Log.W("call GetLicense"); return true; }
        public bool Activate(string code) { Log.W("call Activate(" + code + ")"); return true; }
        public bool Deactivate() { Log.W("call Deactivate"); return true; }
        public string GetLicenseInformation() { Log.W("call GetLicenseInformation"); return "PERPETUAL"; }
        public string GetFeatures() { Log.W("call GetFeatures"); return F; }
        public string GetErrorMessage() { Log.W("call GetErrorMessage"); return ""; }
        public int GetRemainingCopies() { Log.W("call GetRemainingCopies"); return 100; }
    }

    [ComVisible(true)]
    [Guid("330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33")]
    [ProgId("Flexnet.WrapperDongle.DemoLicense")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class DemoLicense
    {
        public DemoLicense() { Log.W("ctor DemoLicense"); }

        public bool IsActivated { get { return Util.G(true); } set { Util.S(value); } }
        public string FeatureName { get { return Util.G(FlexWrapperDongle.F); } set { Util.S(value); } }
        public string ProdNameVersion { get { return Util.G("EFDC_Explorer8.4"); } set { Util.S(value); } }
        public string LicType { get { return Util.G("PERPETUAL"); } set { Util.S(value); } }
        public string ActivationID { get { return Util.G("A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47"); } set { Util.S(value); } }
        public string FulfillmentID { get { return Util.G("14AC1ACA-EFD2-4C01-A1DD-4397B7F19715"); } set { Util.S(value); } }
        public string UniqueId { get { return Util.G("FB5BE307-6E85-410A-9265-B9389E71E38D"); } set { Util.S(value); } }
        public string LicenseFile { get { return Util.G(@"C:\Users\Public\DSI\EEMS8.4\license.lic"); } set { Util.S(value); } }
        public string ExpirationDate { get { return Util.G("2030-01-01"); } set { Util.S(value); } }
        public string VersionDate { get { return Util.G("2030-01-01"); } set { Util.S(value); } }
        public string TotalCopies { get { return Util.G("100"); } set { Util.S(value); } }
        public string RemainingCopies { get { return Util.G("100"); } set { Util.S(value); } }
        public bool IsReportUsage { get { return Util.G(false); } set { Util.S(value); } }
        public string ErrorMessage { get { return Util.G(""); } set { Util.S(value); } }

        public bool CheckLicensing() { Log.W("call Demo.CheckLicensing"); return true; }
        public bool IsLicenseValid() { Log.W("call Demo.IsLicenseValid"); return true; }
        public bool SignIn(string email, string password) { Log.W("call Demo.SignIn(" + email + ")"); return true; }
        public bool Register(string email) { Log.W("call Demo.Register(" + email + ")"); return true; }
        public bool Activate(string code) { Log.W("call Demo.Activate(" + code + ")"); return true; }
        public string GetErrorMessage() { Log.W("call Demo.GetErrorMessage"); return ""; }
    }
}
