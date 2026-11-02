using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Xml;

[assembly: AssemblyVersion("1.0.0.2")]
[assembly: AssemblyFileVersion("1.0.0.2")]
[assembly: AssemblyTitle("DSILIC1 shim")]
[assembly: ComVisible(true)]

namespace Flexnet.WrapperDongle.ShimLog
{
    public static class Log
    {
        static Log() { }
        private static readonly object sync = new object();
        private static readonly string path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "shim_dongle.log");

        private static readonly string[] paths = new string[]
        {
            @"C:\EFDC84_LIC\shim_dongle.log",
            System.IO.Path.Combine(System.IO.Path.GetTempPath(), "shim_dongle.log"),
            @"C:\EFDC84_RUN\shim_dongle.log"
        };

        public static void Write(string s)
        {
            string line = DateTime.Now.ToString("HH:mm:ss.fff") + " " + s + Environment.NewLine;
            lock (sync)
            {
                foreach (string p in paths)
                {
                    try { File.AppendAllText(p, line, Encoding.UTF8); } catch { }
                }
            }
        }

        public static string A(object o)
        {
            if (o == null) return "<null>";
            if (o is string) return "\"" + o + "\"";
            if (o is Array)
            {
                var parts = new List<string>();
                foreach (object x in (Array)o) parts.Add(A(x));
                return "[" + string.Join(",", parts.ToArray()) + "]";
            }
            return Convert.ToString(o, CultureInfo.InvariantCulture);
        }
    }
}

namespace Flexnet.WrapperDongle.Enums
{
    public enum ResultEnum { Success = 0, Fail = 1, Error = 2 }
    public enum InitResultEnum { Success = 0, Fail = 1 }
}

namespace Flexnet.WrapperDongle.Objects
{
    [ComVisible(true)]
    [Guid("B1B2C3D4-0001-4E5F-9A0B-222222222222")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class ForeignData
    {
        public string InnerText { get { return ""; } }
        public string InnerXml { get { return ""; } }
    }

    [ComVisible(true)]
    [Guid("B1B2C3D4-0002-4E5F-9A0B-222222222222")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class XmlResult
    {
        private int _error;
        private string _errorMessage = "";
        private bool _success;
        private XmlDocument _result = new XmlDocument();
        private ForeignData _foreignData = new ForeignData();

        public int error { get { return _error; } set { _error = value; } }
        public string errorMessage { get { return _errorMessage; } set { _errorMessage = value ?? ""; } }
        public ForeignData foreignData { get { return _foreignData; } set { _foreignData = value; } }
        public XmlDocument result { get { return _result; } set { _result = value; } }
        public bool success { get { return _success; } set { _success = value; } }
        public string InnerXml { get { try { return _result == null ? "" : _result.InnerXml; } catch { return ""; } } }
        public string InnerText { get { try { return _result == null ? "" : _result.InnerText; } catch { return ""; } } }

        public static XmlResult Ok(string innerXml)
        {
            var r = new XmlResult();
            r.success = true;
            r.error = 0;
            r._result = new XmlDocument();
            try { r._result.LoadXml(string.IsNullOrEmpty(innerXml) ? "<Response/>" : "<Response>" + innerXml + "</Response>"); }
            catch { r._result.LoadXml("<Response/>"); }
            return r;
        }
    }

    [ComVisible(true)]
    [Guid("B1B2C3D4-0003-4E5F-9A0B-222222222222")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class GetInfoReturnData
    {
        public string activationId { get; set; }
        public string fulfillmentId { get; set; }
        public string state { get; set; }
    }

    [ComVisible(true)]
    [Guid("B1B2C3D4-0004-4E5F-9A0B-222222222222")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class Product
    {
        public string name { get; set; }
        public string version { get; set; }
    }
}

namespace Flexnet.WrapperDongle
{
    [ComVisible(true)]
    [Guid("6399E2C8-63E4-4F31-823C-D256C17E7A13")]
    [ProgId("Flexnet.WrapperDongle.FlexWrapperDongle")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class FlexWrapperDongle : IDisposable
    {
        static FlexWrapperDongle() { ShimLog.Log.Write("== FlexWrapperDongle 类型已加载 =="); }
        public FlexWrapperDongle() { ShimLog.Log.Write("== FlexWrapperDongle 实例已创建 =="); }
        private string _fulfillmentId = "SHIM-DONGLE-FULFILLMENT";
        private bool _initialized;

        private static Objects.XmlResult Call(string name, params object[] args)
        {
            var sb = new StringBuilder();
            sb.Append(name).Append("(");
            for (int i = 0; i < args.Length; i++)
            {
                if (i > 0) sb.Append(", ");
                sb.Append(ShimLog.Log.A(args[i]));
            }
            sb.Append(")");
            ShimLog.Log.Write(sb.ToString());
            return Objects.XmlResult.Ok("<status><message>shim ok</message></status>");
        }

        public string FulfillmentId { get { return _fulfillmentId; } set { _fulfillmentId = value; } }
        public bool JobCreated { get { return true; } }
        public bool Initialized { get { return true; } }

        public string GetNodeLockId() { ShimLog.Log.Write("GetNodeLockId()"); return "NODELOCK-SHIM"; }
        public void Initialize() { _initialized = true; ShimLog.Log.Write("Initialize()"); }
        public void Initialize(string softwarename, string softwareversion, string relNo)
        { _initialized = true; ShimLog.Log.Write("Initialize(" + ShimLog.Log.A(softwarename) + "," + ShimLog.Log.A(softwareversion) + "," + ShimLog.Log.A(relNo) + ")"); }
        public void InitializeSoftware(string softwarename, string softwareversion)
        { _initialized = true; ShimLog.Log.Write("InitializeSoftware(" + ShimLog.Log.A(softwarename) + "," + ShimLog.Log.A(softwareversion) + ")"); }

        public string Decrypt(string strInput) { ShimLog.Log.Write("Decrypt(" + ShimLog.Log.A(strInput) + ")"); return strInput; }
        public string Encrypt(string strInput) { ShimLog.Log.Write("Encrypt(" + ShimLog.Log.A(strInput) + ")"); return strInput; }

        public Objects.XmlResult GetStatus(string feature) { return Call("GetStatus", feature); }
        public Objects.XmlResult CheckIn(string feature) { return Call("CheckIn", feature); }
        public Objects.XmlResult Checkout(string feature, string version) { return Call("Checkout", feature, version); }
        public Objects.XmlResult CheckoutDongleFile(string feature, string version, string licenseFile) { return Call("CheckoutDongleFile", feature, version, licenseFile); }
        public Objects.XmlResult Cleanup() { ShimLog.Log.Write("Cleanup()"); return Objects.XmlResult.Ok(""); }

        public Objects.XmlResult ActivateProduct(string activationId, string nodeLockId, string myLicensePath)
        { return Call("ActivateProduct", activationId, nodeLockId, myLicensePath); }
        public Objects.XmlResult DeActivateProduct(string fulfillmentId, string uniqueId, string activationID)
        { return Call("DeActivateProduct", fulfillmentId, uniqueId, activationID); }

        public Objects.XmlResult GetInfo(string[] activationIds, string[] fullfillmentIds) { return Call("GetInfo", (object)activationIds, (object)fullfillmentIds); }
        public Objects.XmlResult GetInfo2(string activationId, string fulfillmentId) { return Call("GetInfo2", activationId, fulfillmentId); }
        public Objects.XmlResult GetProductInfo2(string activationId, string hostId) { return Call("GetProductInfo2", activationId, hostId); }
        public Objects.XmlResult IsAlreadyActived(string productName, string hostId) { return Call("IsAlreadyActived", productName, hostId); }
        public Objects.XmlResult GenerateMachineId() { ShimLog.Log.Write("GenerateMachineId()"); return Objects.XmlResult.Ok("<machineId>DISK_SERIAL_NUM=2db6323c</machineId>"); }
        public Objects.XmlResult GenerateMachineIdDongle() { ShimLog.Log.Write("GenerateMachineIdDongle()"); return Objects.XmlResult.Ok("<machineId>SHIM-DONGLE</machineId>"); }
        public string GetVersion() { ShimLog.Log.Write("GetVersion()"); return "8.4.3"; }
        public DateTime GetRealTime() { ShimLog.Log.Write("GetRealTime()"); return DateTime.Now; }
        public DateTime GetNistTime() { ShimLog.Log.Write("GetNistTime()"); return DateTime.Now; }
        public bool WebSiteIsAvailable(string Url) { ShimLog.Log.Write("WebSiteIsAvailable(" + Url + ")->true"); return true; }
        public string proxyURL() { ShimLog.Log.Write("proxyURL()"); return "http://127.0.0.1:9/"; }
        public string timeURL() { ShimLog.Log.Write("timeURL()"); return "http://127.0.0.1:9/"; }
        public bool ConnectionAvailable(string strServer) { ShimLog.Log.Write("ConnectionAvailable(" + strServer + ")->true"); return true; }
        public string GetClientInfo() { ShimLog.Log.Write("GetClientInfo()"); return "SHIM"; }
        public void Dispose() { ShimLog.Log.Write("Dispose()"); }
    }

    [ComVisible(true)]
    [Guid("330D13A9-B2BE-4CCF-9B8A-DC2047FB3D33")]
    [ProgId("Flexnet.WrapperDongle.DemoLicense")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class DemoLicense
    {
        static DemoLicense() { ShimLog.Log.Write("== DemoLicense 类型已加载 =="); }
        public void InitializeSoftware(string softwarename, string softwareversion)
        { ShimLog.Log.Write("Demo.InitializeSoftware(" + ShimLog.Log.A(softwarename) + "," + ShimLog.Log.A(softwareversion) + ")"); }

        public string Demo_Activationcode(string email, string hardisk)
        {
            ShimLog.Log.Write("Demo.Demo_Activationcode(" + ShimLog.Log.A(email) + "," + ShimLog.Log.A(hardisk) + ")");
            return "SHIM-DEMO-CODE-0001";
        }

        public Objects.XmlResult SendActivationCode(string email, string fullname) { ShimLog.Log.Write("Demo.SendActivationCode"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult SendNewPassword(string email, string newpwd) { ShimLog.Log.Write("Demo.SendNewPassword"); return Objects.XmlResult.Ok(""); }
        public string GetCoutryCode() { ShimLog.Log.Write("Demo.GetCoutryCode"); return "US"; }

        public Objects.XmlResult SignUp(string email, string password, string firstname, string lastname, string organization, string countrycode, string address, string Occupation, string telephonenumber, string machineId, string product)
        { ShimLog.Log.Write("Demo.SignUp(" + ShimLog.Log.A(email) + ")"); return Objects.XmlResult.Ok(""); }

        public Objects.XmlResult GetUserInfo(string email) { ShimLog.Log.Write("Demo.GetUserInfo(" + ShimLog.Log.A(email) + ")"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult UpdateUserInfo(string email, string firstname, string lastname, string organization, string address, string Occupation, string telephonenumber, string countrycode)
        { ShimLog.Log.Write("Demo.UpdateUserInfo"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult GetMachineId(string email) { ShimLog.Log.Write("Demo.GetMachineId"); return Objects.XmlResult.Ok("<machineId>SHIM-MACHINE</machineId>"); }
        public Objects.XmlResult UpdateMachineId(string email, string machineid) { ShimLog.Log.Write("Demo.UpdateMachineId"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult GetUpgradePackages() { ShimLog.Log.Write("Demo.GetUpgradePackages"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult SignIn(string email, string password) { ShimLog.Log.Write("Demo.SignIn(" + ShimLog.Log.A(email) + ")"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult SignIn2(string email, string machineId) { ShimLog.Log.Write("Demo.SignIn2(" + ShimLog.Log.A(email) + ")"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult EmailExist(string email) { ShimLog.Log.Write("Demo.EmailExist"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult ChangePassword(string email, string oldpassword, string newpassword) { ShimLog.Log.Write("Demo.ChangePassword"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult UpdatePassword(string email, string newpassword) { ShimLog.Log.Write("Demo.UpdatePassword"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult ActivateUser(string email, string activationcode) { ShimLog.Log.Write("Demo.ActivateUser(" + ShimLog.Log.A(email) + "," + ShimLog.Log.A(activationcode) + ")"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult ActivateUser2(string email, string machineId) { ShimLog.Log.Write("Demo.ActivateUser2"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult DeactiveUser2(string email, string machineId) { ShimLog.Log.Write("Demo.DeactiveUser2"); return Objects.XmlResult.Ok(""); }

        public Objects.XmlResult Track_Session(string Email, string model_name, int CellCounts, int Rows, int Cols, int KC, int IGRIDV, DateTime session_start, DateTime session_end, int isDSIModel, string product, int GVC, int ISEDINT)
        { ShimLog.Log.Write("Demo.Track_Session(" + ShimLog.Log.A(model_name) + ")"); return Objects.XmlResult.Ok("<sessionid>SHIM-SESSION</sessionid>"); }
        public Objects.XmlResult Track_UpdateSession(string sessionid, string model_name, int CellCounts, int Rows, int Cols, int KC, int IGRIDV, DateTime session_end, int isDSIModel)
        { ShimLog.Log.Write("Demo.Track_UpdateSession"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_SessionEnd(string sessionid, DateTime sessionend) { ShimLog.Log.Write("Demo.Track_SessionEnd"); return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_Logs(string sessionid, DateTime logtime, string logcontent) { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_MultiLogs(string sessionid, DateTime logtime, string logcontent) { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_MultiLogs_Access() { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_Parameters(string sessionid, int isSalinity, int isTemperature, int isDye, int isShelfish, int isSediments, int isToxics, int isWQ, int isWave, int isLPT) { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_Parameters2(ref string[] pars) { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult Track_SessionModule(string sessionid, string moduleId) { return Objects.XmlResult.Ok(""); }
        public string GetTrack_Modules_ID(string module_type, string module_name) { return "SHIM-MODULE"; }
        public Objects.XmlResult Track_Modules(string sessionid, DateTime logtime, string logcontent) { return Objects.XmlResult.Ok(""); }
        public Objects.XmlResult CreateSurvey(string Email, int a, int b, int c, int d, int e, int f, int g, int h, int i, int j, int k, int l, int m, int n, int o, int p, int q, int r, int s, int t, string suggestion) { return Objects.XmlResult.Ok(""); }
        public bool IsDSIModel(int ActiveIJ, int AREA, int Xc, int Yc, int nTran, int ISTRAN1, int ISTRAN2, int ISTRAN3, int ISTRAN4, int ISTRAN5, int ISTRAN6, int ISTRAN7, int ISTRAN8, int ISTRAN9, int ISTRAN10, int ISTRAN11, int ISTRAN12, string Others) { return false; }
        public Objects.XmlResult CreateFeedback(string Email, int rate, string suggestion) { return Objects.XmlResult.Ok(""); }
        public string ReturnedData(string strXML) { ShimLog.Log.Write("Demo.ReturnedData"); return strXML; }
        public bool IsValidEmail(string email) { return true; }
        public Objects.XmlResult SendEmail(string emailTo, string subject, string body, string logs) { return Objects.XmlResult.Ok(""); }
        public string Encrypt(string txt) { return txt; }
        public string Decrypt(string txt) { return txt; }
    }
}




