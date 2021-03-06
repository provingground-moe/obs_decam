
import collections.abc
import re
from lsst.pipe.tasks.ingestCalibs import CalibsParseTask

__all__ = ["DecamCalibsParseTask"]


class DecamCalibsParseTask(CalibsParseTask):

    def getInfo(self, filename):
        """Get information about the image from the filename and/or its contents.

        Parameters
        ----------
        filename: `str`
            Name of file to inspect.

        Returns
        -------
        phuInfo : `dict`
            Primary header unit info.
        infoList : `list` of `dict`
            File properties; list of file properties for each extension.
        """
        phuInfo, infoList = CalibsParseTask.getInfo(self, filename)
        # Single-extension fits without EXTNAME can be a valid CP calibration product
        # Use info of primary header unit
        if not infoList:
            infoList.append(phuInfo)
        for info in infoList:
            info['path'] = filename
        # Try to fetch a date from filename
        # and use as the calibration dates if not already set
        found = re.search(r'(\d\d\d\d-\d\d-\d\d)', filename)
        for item in infoList:
            try:
                item['calib_hdu'] = item['hdu']
            except KeyError:  # workaround for pre- DM-19730 defect ingestion
                item['calib_hdu'] = 1
        if not found:
            return phuInfo, infoList
        date = found.group(1)
        for info in infoList:
            if 'calibDate' not in info or info['calibDate'] == "unknown":
                info['calibDate'] = date
        return phuInfo, infoList

    def _translateFromCalibId(self, field, md):
        """Fetch the ID from the CALIB_ID header.

        Calibration products made with constructCalibs have some metadata
        saved in its FITS header CALIB_ID.
        """
        data = md.getScalar("CALIB_ID")
        match = re.search(r".*%s=(\S+)" % field, data)
        return match.groups()[0]

    def translate_ccdnum(self, md):
        """Return CCDNUM as a integer.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            FITS header metadata.
        """
        if md.exists("CCDNUM"):
            ccdnum = md.getScalar("CCDNUM")
        else:
            return self._translateFromCalibId("ccdnum", md)
        # Some MasterCal from NOAO Archive has 2 CCDNUM keys in each HDU
        # Make sure only one integer is returned.
        if isinstance(ccdnum, collections.abc.Sequence):
            try:
                ccdnum = ccdnum[0]
            except IndexError:
                ccdnum = None
        return ccdnum

    def translate_date(self, md):
        """Extract the date as a strong in format YYYY-MM-DD from the FITS header DATE-OBS.
        Return "unknown" if the value cannot be found or converted.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            FITS header metadata.
        """
        if md.exists("DATE-OBS"):
            date = md.getScalar("DATE-OBS")
            found = re.search(r'(\d\d\d\d-\d\d-\d\d)', date)
            if found:
                date = found.group(1)
            else:
                self.log.warn("DATE-OBS does not match format YYYY-MM-DD")
                date = "unknown"
        elif md.exists("CALIB_ID"):
            date = self._translateFromCalibId("calibDate", md)
        else:
            date = "unknown"
        return date

    def translate_filter(self, md):
        """Extract the filter name.

        Translate a full filter description into a mere filter name.
        Return "unknown" if the keyword FILTER does not exist in the header,
        which can happen for some valid Community Pipeline products.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            FITS header metadata.
        """
        if md.exists("FILTER"):
            if md.exists("OBSTYPE") and "zero" in md.getScalar("OBSTYPE").strip().lower():
                return "NONE"
            return CalibsParseTask.translate_filter(self, md)
        elif md.exists("CALIB_ID"):
            return self._translateFromCalibId("filter", md)
        else:
            return "unknown"

    @staticmethod
    def getExtensionName(md):
        """Get the name of the extension.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            FITS header metadata.

        Returns
        -------
        result : `str`
            The string from the EXTNAME header card.
        """
        return md.getScalar('EXTNAME')

    def getDestination(self, butler, info, filename):
        """Get destination for the file.

        Parameters
        ----------
        butler : `lsst.daf.persistence.Butler`
            Data butler.
        info : data ID
            File properties, used as dataId for the butler.
        filename : `str`
            Input filename.

        Returns
        -------
        raw : `str`
            Destination filename.
        """
        # Arbitrarily set ccdnum and calib_hdu to 1 to make the mapper template happy
        info["ccdnum"] = 1
        info["calib_hdu"] = 1
        calibType = self.getCalibType(filename)
        if "flat" in calibType.lower():
            raw = butler.get("cpFlat_filename", info)[0]
        elif ("bias" or "zero") in calibType.lower():
            raw = butler.get("cpBias_filename", info)[0]
        elif ("illumcor") in calibType.lower():
            raw = butler.get("cpIllumcor_filename", info)[0]
        else:
            assert False, "Invalid calibType '{:s}'".format(calibType)
        # Remove HDU extension (ccdnum) since we want to refer to the whole file
        c = raw.find("[")
        if c > 0:
            raw = raw[:c]
        return raw
