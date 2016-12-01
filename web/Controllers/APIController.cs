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
using web;

namespace WebApplication.Controllers
{
    [Route("api/temperature")]
    public class APIController : Controller
    {
        private ApplicationDbContext context;
        public APIController(ApplicationDbContext context) {
            this.context = context;
        }

        [HttpGet()]
        public Temperature Get() {
            var temperature = context.Temperatures.OrderByDescending(t => t.TimeStamp).First();
            return temperature;
        }
    }


}
