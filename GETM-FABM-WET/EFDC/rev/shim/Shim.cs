using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Xml;

[assembly: AssemblyVersion("1.0.0.1")]
[assembly: AssemblyFileVersion("1.0.0.1")]
[assembly: AssemblyTitle("DSILIC0 shim")]
[assembly: ComVisible(true)]

namespace Flexnet.Wrapper.ShimLog
{
    public static class Log
    {
        private static readonly object sync = new object();
        private static string path = @"C:\EFDC84_LIC\shim_calls.log";

        public static void Write(string s)
        {
            try
            {
                lock (sync)
                {
                    File.AppendAllText(path,
                        DateTime.Now.ToString("HH:mm:ss.fff") + " " + s + Environment.NewLine,
                        Encoding.UTF8);
                }
            }
            catch { }
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

namespace Flexnet.Wrapper.Enums
{
    public enum ResultEnum { Success = 0, Fail = 1, Error = 2 }
    public enum InitResultEnum { Success = 0, Fail = 1 }
}

namespace Flexnet.Wrapper.Objects
{
    [ComVisible(true)]
    [Guid("A1B2C3D4-0001-4E5F-9A0B-111111111111")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class ForeignData
    {
        public string InnerText { get { return ""; } }
        public string InnerXml { get { return ""; } }
    }

    [ComVisible(true)]
    [Guid("A1B2C3D4-0002-4E5F-9A0B-111111111111")]
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

        public string InnerXml
        {
            get { try { return _result == null ? "" : _result.InnerXml; } catch { return ""; } }
        }

        public string InnerText
        {
            get { try { return _result == null ? "" : _result.InnerText; } catch { return ""; } }
        }

        public static XmlResult Ok(string innerXml)
        {
            var r = new XmlResult();
            r.success = true;
            r.error = 0;
            r.errorMessage = "";
            r._result = new XmlDocument();
            if (!string.IsNullOrEmpty(innerXml))
            {
                try { r._result.LoadXml("<Response>" + innerXml + "</Response>"); }
                catch { r._result.LoadXml("<Response/>"); }
            }
            else
            {
                r._result.LoadXml("<Response/>");
            }
            return r;
        }
    }

    [ComVisible(true)]
    [Guid("A1B2C3D4-0003-4E5F-9A0B-111111111111")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class Product
    {
        public string name { get; set; }
        public string version { get; set; }
    }

    [ComVisible(true)]
    [Guid("A1B2C3D4-0004-4E5F-9A0B-111111111111")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class GetInfoReturnData
    {
        public string activationId { get; set; }
        public string fulfillmentId { get; set; }
        public string state { get; set; }
    }
}

namespace Flexnet.Wrapper
{
    [ComVisible(true)]
    [Guid("E326A913-D0B1-44E2-8015-952959CEA45F")]
    [ProgId("Flexnet.Wrapper.FlexWrapper")]
    [ClassInterface(ClassInterfaceType.AutoDual)]
    public class FlexWrapper : IDisposable
    {
        private string _fulfillmentId = "SHIM-FULFILLMENT-0001";
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
        public bool JobCreated { get { return false; } }
        public bool Initialized { get { return _initialized; } }

        public string GetNodeLockId()
        {
            ShimLog.Log.Write("GetNodeLockId()");
            return "NODELOCK-SHIM-0001";
        }

        public void Initialize()
        {
            _initialized = true;
            ShimLog.Log.Write("Initialize()");
        }

        public void InitializeSoftware(string softwarename, string softwareversion)
        {
            _initialized = true;
            ShimLog.Log.Write("InitializeSoftware(" + ShimLog.Log.A(softwarename) + ", " + ShimLog.Log.A(softwareversion) + ")");
        }

        public Objects.XmlResult GetStatus(string feature) { return Call("GetStatus", feature); }
        public Objects.XmlResult Checkout(string feature, string version) { return Call("Checkout", feature, version); }
        public Objects.XmlResult CheckoutLicensefile(string feature, string version, string licenseFile) { return Call("CheckoutLicensefile", feature, version, licenseFile); }
        public Objects.XmlResult CheckIn(string feature) { return Call("CheckIn", feature); }
        public Objects.XmlResult Cleanup() { ShimLog.Log.Write("Cleanup()"); return Objects.XmlResult.Ok(""); }

        public Objects.XmlResult ActivateProduct(string activationId, string nodeLockId, string myLicensePath, string clientlicenseInfo, string soldto, string product)
        { return Call("ActivateProduct", activationId, nodeLockId, myLicensePath, clientlicenseInfo, soldto, product); }

        public Objects.XmlResult DeActivateProduct(string fulfillmentId, string uniqueId, string soldto, string product)
        { return Call("DeActivateProduct", fulfillmentId, uniqueId, soldto, product); }

        public Objects.XmlResult GetInfo(string[] activationIds, string[] fullfillmentIds)
        { return Call("GetInfo", (object)activationIds, (object)fullfillmentIds); }

        public Objects.XmlResult GetInfo2(string activationId, string fullfillmentId) { return Call("GetInfo2", activationId, fullfillmentId); }
        public Objects.XmlResult GetProductInfo2(string activationId, string hostId) { return Call("GetProductInfo2", activationId, hostId); }
        public Objects.XmlResult IsAlreadyActived(string productName, string hostId) { return Call("IsAlreadyActived", productName, hostId); }
        public Objects.XmlResult GenerateMachineId() { ShimLog.Log.Write("GenerateMachineId()"); return Objects.XmlResult.Ok("<machineId>SHIM-MACHINE-0001</machineId>"); }
        public Objects.XmlResult GenerateMachineIdDongle() { ShimLog.Log.Write("GenerateMachineIdDongle()"); return Objects.XmlResult.Ok("<machineId>SHIM-DONGLE-0001</machineId>"); }
        public string GetVersion() { ShimLog.Log.Write("GetVersion()"); return "8.4.0.0"; }

        public DateTime GetRealTime() { ShimLog.Log.Write("GetRealTime()"); return DateTime.Now; }
        public DateTime GetNistTime() { ShimLog.Log.Write("GetNistTime()"); return DateTime.Now; }
        public bool WebSiteIsAvailable(string Url) { ShimLog.Log.Write("WebSiteIsAvailable(" + Url + ") -> true"); return true; }
        public bool ConnectionAvailable(string strServer) { ShimLog.Log.Write("ConnectionAvailable(" + strServer + ") -> true"); return true; }
        public string GetClientInfo() { ShimLog.Log.Write("GetClientInfo()"); return "SHIM"; }

        public System.Data.DataTable getActivatableItems(string productName, DateTime from, DateTime to, int type, int batchSize)
        {
            ShimLog.Log.Write("getActivatableItems(" + productName + ")");
            var t = new System.Data.DataTable();
            t.Columns.Add("activationId");
            return t;
        }

        public Objects.XmlResult UpdateActivatableItems(int type, string entitlementId, string activationId, DateTime start, DateTime end)
        { return Call("UpdateActivatableItems", type, entitlementId, activationId, start, end); }

        public void Dispose() { ShimLog.Log.Write("Dispose()"); }
    }
}
