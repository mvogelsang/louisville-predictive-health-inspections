using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using WebApplication1.DataContext;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace WebApplication1.Controllers
{
    public class HealthInspectionsController : Controller
    {
        // GET: HealthInspections
        public ActionResult Index()
        {
            GetJsonData var = new GetJsonData();
            var jobject = JsonConvert.DeserializeObject<RootObject>(var.GetData().ToString());
            return View(jobject.courses);
        }
    }
}