#!/usr/bin/env/python
#-*- coding:utf-8 -*-

__author__ = 'BlackYe.'

from ...libs.core.globaldata import conf, vulresult, source_result, db_audit
from ...models.auditdb import AuditMysqlDB
from ...models.scan_vuldetail import ScanVulDetail
from ...data import Data
from ...data.resource.domain import Domain
from ...data.resource.ip import IP
from ...data.resource.url import BaseURL, URL
from ...data.vuln.vulnerability import WebVulnerability

from ...utils.console_utils import get_terminal_size, colorize_substring, colorize
from ...utils.mytime import MyTime
from ...utils import _str2bs64

from thirdparty_libs.texttable import Texttable
from thirdparty_libs.prettytable.prettytable import PrettyTable


import sys
from collections import defaultdict

class TextReport():

    #--------------------------------------------------------------------------
    def generate_report(self):
        self.__show_data = True
        self.__console = True
        self.__color   = True #Console.use_colors
        self.__width   = max(0, get_terminal_size()[0])
        self.__fd      = sys.stdout
        self.__write_report()

    #--------------------------------------------------------------------------
    def __write_report(self):

        # Header
        print >>self.__fd, ""
        print >>self.__fd, "--= %s =--" % self.__colorize("Report", "cyan")
        print >>self.__fd, ""

        # Summary
        #start_time, stop_time, run_time = parse_audit_times( *get_audit_times() )
        start_time, stop_time, run_time = MyTime.parse_audit_times(source_result.start_time, source_result.end_time)

        #host_count  = Database.count(Data.TYPE_RESOURCE, Domain.data_subtype)
        #host_count += Database.count(Data.TYPE_RESOURCE, IP.data_subtype)
        #vuln_count  = Database.count(Data.TYPE_VULNERABILITY)
        host_count = 2
        #vuln_count = 3
        print >>self.__fd, "-# %s #- " % self.__colorize("Summary", "yellow")
        print >>self.__fd, ""
        print >>self.__fd, "Audit started:   %s" % self.__colorize(start_time, "yellow")
        print >>self.__fd, "Audit ended:     %s" % self.__colorize(stop_time, "yellow")
        print >>self.__fd, "Execution time:  %s" % self.__colorize(run_time, "yellow")
        print >>self.__fd, ""
        print >>self.__fd, "Scanned hosts:   %s" % self.__colorize(str(host_count), "yellow")
        #print >>self.__fd, "Vulnerabilities: %s" % self.__colorize(str(vuln_count), "red" if vuln_count else "yellow")
        print >>self.__fd, ""

        '''
        # Audit scope
        if self.__show_data or not self.__console:
            table = Texttable()
            scope_domains = conf.audit_scope.roots
            if conf.audit_scope.addresses:
                table.add_row(("IP addresses", conf.audit_scope.addresses))
            if scope_domains:
                table.add_row(("Domains", scope_domains))
            if conf.audit_scope.web_pages:
                table.add_row(("Web pages", conf.audit_scope.web_pages))

            if table._rows:
                self.__fix_table_width(table)
                print >>self.__fd, "-# %s #- " % self.__colorize("Audit Scope", "yellow")
                print >>self.__fd, ""
                print >>self.__fd, table.draw()
                print >>self.__fd, ""
        '''
        '''
        # Discovered hosts
        if self.__show_data:
            need_header = True
            for domain in self.__iterate(Data.TYPE_RESOURCE, Domain.data_subtype):
                table = Texttable()
                #self.__add_related(table, domain, Data.TYPE_INFORMATION, Geolocation.data_subtype, "Location")
                #self.__add_related(table, domain, Data.TYPE_INFORMATION, WebServerFingerprint.data_subtype, "Web Server")
                #self.__add_related(table, domain, Data.TYPE_INFORMATION, OSFingerprint.data_subtype, "OS Fingerprint")
                if table._rows:
                    if need_header:
                        need_header = False
                        print >>self.__fd, "-# %s #- " % self.__colorize("Hosts", "yellow")
                        print >>self.__fd, ""
                    table.header(("Domain Name", domain.hostname))
                    self.__fix_table_width(table)
                    text = table.draw()
                    if self.__color:
                        text = colorize_substring(text, domain.hostname, "red" if domain.get_links(Data.TYPE_VULNERABILITY) else "green")
                    print >>self.__fd, text
                    print >>self.__fd, ""
            for ip in self.__iterate(Data.TYPE_RESOURCE, IP.data_subtype):
                table = Texttable()
                self.__add_related(table, ip, Data.TYPE_RESOURCE, Domain.data_subtype, "Domain Name")
                if table._rows:
                    if need_header:
                        need_header = False
                        print >>self.__fd, "-# %s #- " % self.__colorize("Hosts", "yellow")
                        print >>self.__fd, ""
                    table.header(("IP Address", ip.address))
                    self.__fix_table_width(table)
                    text = table.draw()
                    if self.__color:
                        text = colorize_substring(text, ip.address, "red" if ip.get_links(Data.TYPE_VULNERABILITY) else "green")
                    print >>self.__fd, text
                    print >>self.__fd, ""

        # Web servers
        if self.__show_data and 1:
            print >>self.__fd, "-# %s #- " % self.__colorize("Web Servers", "yellow")
            print >>self.__fd, ""
            crawled = defaultdict(list)
            vulnerable = []
            for url in self.__iterate(Data.TYPE_RESOURCE, URL.data_subtype):
                crawled[url.hostname].append(url.url)
                if self.__color and url.get_links(Data.TYPE_VULNERABILITY):
                    vulnerable.append(url)
            for url in self.__iterate(Data.TYPE_RESOURCE, BaseURL.data_subtype):
                table = Texttable()
                table.header(("Base URL", url.url))
                #self.__add_related(table, url, Data.TYPE_INFORMATION, WebServerFingerprint.data_subtype, "Server")
                #self.__add_related(table, url, Data.TYPE_INFORMATION, OSFingerprint.data_subtype, "Platform")
                urls = crawled[url.hostname]
                if urls:
                    urls.sort()
                    table.add_row(("Visited URLs", "\n".join(urls)))
                if table._rows:
                    self.__fix_table_width(table)
                    text = table.draw()
                    if self.__color:
                        p = text.find("\n")
                        p = text.find("\n", p + 1)
                        p = text.find("\n", p + 1)
                        if p > 0:
                            text = colorize_substring(text[:p], url.url, "red" if url.get_links(Data.TYPE_VULNERABILITY) else "green") + text[p:]
                        for u in vulnerable:
                            if u != url.url:
                                text = colorize_substring(text, u, "red")
                    print >>self.__fd, text
                    print >>self.__fd, ""
        '''

        # Vulnerabilities
        print >>self.__fd, "-# %s #- " % self.__colorize("Vulnerabilities", "yellow")
        print >>self.__fd, ""
        #count = Database.count(Data.TYPE_VULNERABILITY)
        count = vulresult.qsize()
        if count:
            if self.__show_data:
                print >>self.__fd, self.__colorize("%d vulnerabilities found!" % count, "red")
                print >>self.__fd, ""

            if vulresult.qsize() > 0:
                table = Texttable()
                table.add_row(["Vul Type", "Vul Url", "Vul Parameter", "Payload", "Method", "Risk Level"])

                while vulresult.qsize() > 0:
                    _ = vulresult.get()
                    table.add_row([_.injection_type,
                                   _.url,
                                   _.vulparam_point,
                                   _.payload,
                                   _.vul_method,
                                   _.vul_risk_desc]
                                  )

                    #audit_db insert scan result into db
                    vul_detail = ScanVulDetail(st_id          = source_result.task_id,
                                               sli_id         = _.vul_sli_id,
                                               url            = _.url,
                                               vulparam_point = _.vulparam_point,
                                               method         = _.vul_method,
                                               payload        = _.payload,
                                               get_param      = None,
                                               post_param     = None,
                                               ori_req_header = _str2bs64(_.vul_response.raw_request.headers.get_headers()),
                                               ori_resp_header= _str2bs64(str(_.vul_response.headers.get_headers())),
                                               ori_resp_body  = _str2bs64(_.vul_response.data),
                                               insert_time    = MyTime.get_current_datetime()
                                             )
                    db_audit.session.add(vul_detail)
                    db_audit.session.commit()

                self.__fix_vul_table_width(table)
                text = table.draw()

                print >>self.__fd, text
                print >>self.__fd, ""

        else:
            print >>self.__fd, self.__colorize("No vulnerabilities found.", "green")
            print >>self.__fd, ""


    #--------------------------------------------------------------------------
    def __gather_vulnerable_resources(self, vuln):
        vulnerable = []
        visited = set()
        queue = [vuln]
        while queue:
            data = queue.pop()
            identity = data.identity
            if identity not in visited:
                visited.add(identity)
                if data.data_type == Data.TYPE_RESOURCE:
                    vulnerable.append(str(data))
                else:
                    queue.extend(data.linked_data)
        visited.clear()
        return vulnerable

    #--------------------------------------------------------------------------
    def __colorize(self, txt, level_or_color):
        if self.__color:
            return colorize(txt, level_or_color)
        return txt

    #--------------------------------------------------------------------------
    def __fix_table_width(self, table):
        if self.__width > 0:
            if hasattr(table, "_hline_string"):
                table._hline_string = "" # workaround for bug in texttable
            assert all(len(x) == 2 for x in table._rows), table._rows
            w = max( len(x[0]) for x in table._rows )
            if table._header:
                assert len(table._header) == 2, len(table._header)
                w = max( w, len(table._header[0]) )
            m = w + 8
            if self.__width > m:
                table.set_cols_width((w, self.__width - m))

    def __fix_vul_table_width(self, table):
        if self.__width > 0:
            if hasattr(table, "_hline_string"):
                table._hline_string = "" # workaround for bug in texttable
            assert all(len(x) == 6 for x in table._rows), table._rows
            w = max( len(x[0]) for x in table._rows )
            if table._header:
                assert len(table._header) == 6, len(table._header)
                w = max( w, len(table._header[0]) )
            m = w + 8
            if self.__width > m:
                vulurl_width    = m + 40
                parameter_width = 20
                payload_width   = 10
                method_width    = 10
                risk_width      = 10
                table.set_cols_width((w, vulurl_width, parameter_width, payload_width, method_width, risk_width))

