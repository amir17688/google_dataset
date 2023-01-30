from cl.generator.encoderclgenerator import EncoderCLGenerator
from cl.util.clstringutils import CLStringUtils
from stream.videostream import VideoStream
from stream.audiostream import AudioStream


class FFMPEGCLGenerator(EncoderCLGenerator):
    """
    FFMPEG Command Line Interface Buider
    """

    ENCODER_VIDEO_FORMAT_COPY = "copy"
    """
    Encodes video's output with same codec as same input's video codec
    """

    ENCODER_AUDIO_FORMAT_COPY = "copy"
    """
    Encodes audio's output with same codec as same input's audio codec
    """

    def __init__(self):
        """
        Constructor
        """
        super(FFMPEGCLGenerator, self).__init__()
        self._program = "ffmpeg"
        self._overwiteOutputFileWithoutAsking = None
        self._outputVideoCodec = None
        self._outputAudioCodec = None
        self._ouputVideoFrameRate = None

    def getInput():
        """
        Returns input as list if any.
        @return List or None
        """
        return None

    def addInputFile(self, filename):
        """
        Adds input file.
        @param filename Path to filename
        @return self
        """
        self._inputFiles.append(filename)
        return self

    def addOutputFile(self, filename):
        """
        Adds output file.
        @param filename Path to filename
        @return self
        """
        self._outputFiles.append(filename)
        return self

    def addOverwriteOutputFileWithoutAsking(self):
        """
        Adds overwrite output file without asking.
        @return self
        """
        self._overwiteOutputFileWithoutAsking = "-y"
        return self

    def addOutputVideoCodec(self, codec):
        """
        Adds output video codec.
        @param: codec Any ENCODER_VIDEO_FORMAT_*
        @return self
        """
        self._outputVideoCodec = CLStringUtils.concatStrings("-vcodec ", codec)
        return self

    def addOutputVideoFramerate(self, framerate):
        """
        Adds output video framerate.
        @param: framerate Framerate as string value
        @return self
        """
        value = CLStringUtils.concatStrings("-r ", framerate)
        self._ouputVideoFrameRate = value
        return self

    def addOutputAudioCodec(self, codec):
        """
        Adds output audio codec.
        @param: codec Any ENCODER_AUDIO_FORMAT_*
        @return self
        """
        self._outputAudioCodec = CLStringUtils.concatStrings("-acodec ", codec)
        return self

    def buildCL(self):
        cli = CLStringUtils.concatStringsUnlessNone("", self._program)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        value0 = self._overwiteOutputFileWithoutAsking
        cli = CLStringUtils.concatStringsUnlessNone(cli, value0)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        value1 = self._outputVideoCodec
        cli = CLStringUtils.concatStringsUnlessNone(cli, value1)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        value2 = self._outputAudioCodec
        cli = CLStringUtils.concatStringsUnlessNone(cli, value2)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        # Take only one input file
        value5 = ""
        if (len(self._inputFiles) > 0):
            value5 = self._inputFiles[0]
        value5 = CLStringUtils.concatStrings("-i ", value5)
        cli = CLStringUtils.concatStringsUnlessNone(cli, value5)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        value3 = self._ouputVideoFrameRate
        cli = CLStringUtils.concatStringsUnlessNone(cli, value3)
        cli = CLStringUtils.concatStringsUnlessNone(cli, " ")
        # Take only one output file
        value6 = ""
        if (len(self._outputFiles) > 0):
            value6 = self._outputFiles[0]
        value6 = CLStringUtils.concatStrings("", value6)
        cli = CLStringUtils.concatStringsUnlessNone(cli, value6)
        return cli

    @staticmethod
    def createFrom(sourceMediaFile=None, destinationMediaFile=None):
        """
        Creates a FFMPEGCLIBuilder instance from both media files
        @param sourceMediaFile Source MediaFile object
        @param destinationMediaFile Destination MediaFile object
        @return FFMPEGCLIBuilder instance
        """
        ffmpegclgenerator = FFMPEGCLGenerator()
        iVideoStreams = sourceMediaFile.getVideoStreams()
        iAudioStreams = sourceMediaFile.getAudioStreams()
        oVideoStreams = destinationMediaFile.getVideoStreams()
        oAudioStreams = destinationMediaFile.getAudioStreams()

        # Process input media file
        ffmpegclgenerator.addInputFile(sourceMediaFile.getFileName())

        # Process output media file
        for dV in oVideoStreams:
            if dV.getCodecName() != None:
                ffmpegclgenerator.addOutputVideoCodec(dV.getCodecName())

        for dV in oAudioStreams:
            if dV.getCodecName() != None:
                ffmpegclgenerator.addOutputAudioCodec(dV.getCodecName())

        ffmpegclgenerator.addOutputFile(destinationMediaFile.getFileName())
        return ffmpegclgenerator

    def getCompletedReturnCode(self):
        return 0
