using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using WebApplication.Data;
using WebApplication.Models;
using WebApplication.Models.ManageViewModels;
using WebApplication.Services;

namespace WebApplication.Controllers
{
    public class HomeController : Controller
    {
        private ApplicationDbContext context;
        public HomeController(ApplicationDbContext context) {
            this.context = context;
        }

        public IActionResult Index() {
            var temperature = context.Temperatures.OrderByDescending(t => t.TimeStamp).First();
            return View(temperature);
        }
    }


}
