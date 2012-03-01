#ifndef DM_LOG_H
#define DM_LOG_H

/**
 * @file
 * Logging functions. If DLIB_LOG_DOMAIN is defined the value of the defined is printed
 * after severity. Otherwise DEFAULT will be printed.
 *
 * Network protocol:
 * When connected a message with the following syntax is sent to the client
 * code <space> msg\n
 * eg 0 OK\n
 *
 * code > 0 indicates an error and the connections is closed by remote peer
 *
 * After connection is established log messages are streamed over the socket.
 * No other messages with semantic meaning is sent.
 */

/**
 * Log severity
 */
enum dmLogSeverity
{
    DM_LOG_SEVERITY_DEBUG   = 0,//!< DM_LOG_SEVERITY_DEBUB
    DM_LOG_SEVERITY_INFO    = 1,//!< DM_LOG_SEVERITY_INFO
    DM_LOG_SEVERITY_WARNING = 2,//!< DM_LOG_SEVERITY_WARNING
    DM_LOG_SEVERITY_ERROR   = 3,//!< DM_LOG_SEVERITY_ERROR
    DM_LOG_SEVERITY_FATAL   = 4,//!< DM_LOG_SEVERITY_FATAL
};

#ifdef DM_LOG_DISABLE

#define dmLogInfo(format, args...) do {} while(0);
#define dmLogWarning(format, args...) do {} while(0);
#define dmLogError(format, args...) do {} while(0);
#define dmLogFatal(format, args...) do {} while(0);

#else

#ifndef DLIB_LOG_DOMAIN
#define DLIB_LOG_DOMAIN "DEFAULT"
#ifdef __GNUC__
#warning "DLIB_LOG_DOMAIN is not defined"
#endif
#endif

#ifdef __GNUC__
void dmLogInternal(dmLogSeverity severity, const char* domain, const char* format, ...)
    __attribute__ ((format (printf, 3, 4)));
#else
void dmLogInternal(dmLogSeverity severity, const char* domain, const char* format, ...);
#endif

#ifdef _MSC_VER
#define dmLogDebug(format, ... ) dmLogInternal(DM_LOG_SEVERITY_DEBUG, DLIB_LOG_DOMAIN, format, __VA_ARGS__ );
#define dmLogInfo(format, ... ) dmLogInternal(DM_LOG_SEVERITY_INFO, DLIB_LOG_DOMAIN, format, __VA_ARGS__ );
#define dmLogWarning(format, ... ) dmLogInternal(DM_LOG_SEVERITY_WARNING, DLIB_LOG_DOMAIN, format, __VA_ARGS__ );
#define dmLogError(format, ... ) dmLogInternal(DM_LOG_SEVERITY_ERROR, DLIB_LOG_DOMAIN, format, __VA_ARGS__ );
#define dmLogFatal(format, ... ) dmLogInternal(DM_LOG_SEVERITY_FATAL, DLIB_LOG_DOMAIN, format, __VA_ARGS__ );
#else
#define dmLogDebug(format, args...) dmLogInternal(DM_LOG_SEVERITY_DEBUG, DLIB_LOG_DOMAIN, format, ## args);
#define dmLogInfo(format, args...) dmLogInternal(DM_LOG_SEVERITY_INFO, DLIB_LOG_DOMAIN, format, ## args);
#define dmLogWarning(format, args...) dmLogInternal(DM_LOG_SEVERITY_WARNING, DLIB_LOG_DOMAIN, format, ## args);
#define dmLogError(format, args...) dmLogInternal(DM_LOG_SEVERITY_ERROR, DLIB_LOG_DOMAIN, format, ## args);
#define dmLogFatal(format, args...) dmLogInternal(DM_LOG_SEVERITY_FATAL, DLIB_LOG_DOMAIN, format, ## args);
#endif

#endif

/**
 * Initialize logging system. Running this function is only required in order to start the log-server.
 * The function will never fail even if the log-server can't be started. Any errors will be reported to stderr though
 */
void dmLogInitialize();


/**
 * Finalize logging system
 */
void dmLogFinalize();

/**
 * Get log server port
 * @return server port. 0 if the server isn't started.
 */
uint16_t dmLogGetPort();


/**
 * Set log level
 * @param severity Log severity
 */
void dmLogSetlevel(dmLogSeverity severity);

#endif // DM_LOG_H
