type LoggerType = 
    "info"  |
    "debug" |
    "error" |
    "warn"

class Logger {
    formatString: String = "";

    constructor(name: string) {
        this.formatString = `[${name.toUpperCase()}]`
    }

    format(type: LoggerType) {
        return `${this.formatString} | ${type.toUpperCase()} | `
    }

    info(message: string) {
        console.log(this.format("info") + message)
    }

    debug(message: string) {
        console.log(this.format("debug") + message)
    }

    error(message: string) {
        console.log(this.format("error") + message)
    }
    
    warn(message: string) {
        console.log(this.format("warn") + message)
    }
}


export default Logger;