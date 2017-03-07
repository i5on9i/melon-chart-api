#encoding=utf-8


from datetime import datetime, timedelta
import requests
from lxml import etree
from io import StringIO, BytesIO


class ChartType(object):
    WEEK = "WE"

class MelonChart(object):
    melonSearchChartUrl = "http://www.melon.com/chart/search/list.htm"

    def __init__(self):
        self.tree = None

    def getChart(self, sdate):
        """
            Retrieve the chart list between {sdate} and {edate}
            Then, set {self.tree}

            :param sdate datetime
            :param edate datetime
        """
        adjSdate, adjEdate = self._adjustedDate(sdate)
        sdateStr = adjSdate.strftime("%Y%m%d")
        edateStr = adjEdate.strftime("%Y%m%d")
        dayVal = "{sdate}^{edate}"\
                .format(sdate=sdateStr, edate=edateStr)
        
        ageVal = sdate.year // 10 * 10

        options = {
            "chartType" : ChartType.WEEK,
            "age" : ageVal,
            "year" : adjSdate.year,
            "mon" : "%02d"%(adjSdate.month,),
            "day" : dayVal, # "20160307%5E20160313"
            "classCd" : "DP0100",
            "startDay" : sdateStr,
            "endDay" : edateStr,
            "moved" : "Y",
        }
        r = requests.get(self.melonSearchChartUrl, params=options)
        if r.status_code != 200:
            raise requests.RequestException()
        
        # self._saveAsFile(r.content)
        content = r.content.decode('utf-8')
        parser = etree.HTMLParser()
        self.tree   = etree.parse(StringIO(content), parser)

        return self

    def _adjustedDate(self, sdate):
        """
            :return 
                Returns the first Monday when the sdate is later than 2012-08-06,
                or the first Sunday when the sdate is earlier than 2012-08-06
                when the sdate is 2012-08-06, 2012-08-13 is returned

            Aug. 2012
            |Sun.| ...
             <------------------------------|
            | 5  | 6  | 7 | 8 | 9 | 10 | 11 |
            | 12 | 13 |-->
            # 2012-08-05 -> 2012-08-13
        """
        weekday = sdate.weekday()
        if sdate > datetime(2012, 8, 6) and weekday != 0:
            # After the start-date is 2012-08-06, 
            # the weekday of the start date should be Monday
            sdate += timedelta(days=0-weekday+7) # the next first Mon.

        elif sdate == datetime(2012, 8, 6):
            sdate = datetime(2012, 8, 13)

        elif sdate < datetime(2012, 8, 6) and weekday != 6:
            # Before the start-date is 2012-08-06, 
            # the Sun. is the start day of the week chart
            sdate += timedelta(days=6-weekday) # the next first Mon.

        return sdate, sdate+timedelta(days=6)





    def _saveAsFile(self, content):
        with open('r.htm', 'w+') as wf:
            wf.write(content.decode('utf-8'))
        
    def getRank(self, title):
        """
            :return rank int
        """
        
        tree = self.tree
        xpath = '//a[contains(text(), "{title}")]/ancestor::tr'.format(title=title)
        tr = tree.xpath(xpath)
        if len(tr) == 0:
            return None
        ranks = tr[0].xpath('.//span[contains(@class, "rank")]')
        
        return int(ranks[0].text)


def main():
    melonSearchChartUrl = "http://www.melon.com/chart/search/list.htm"

    import time

    # 2012-08-05 -> 2012-08-13
    sdate = datetime(2016, 2, 28)
    edate = datetime(2017, 2, 27)
    # sdate = datetime(2016, 5, 23)
    # edate = datetime(2016, 5, 29)
    tdelta = timedelta(days=7)
    tdelta2 = timedelta(days=6)
    
    mchart = MelonChart()
    csdate = sdate
    cedate = csdate + tdelta2
    while cedate <= edate:

        rank = mchart.getChart(csdate).getRank("벚꽃 엔딩")
        print("{sdate},{rank}".format(sdate=csdate, rank=rank))

        csdate = csdate + tdelta
        cedate = csdate + tdelta2
        



    

if __name__ == '__main__':
    main()