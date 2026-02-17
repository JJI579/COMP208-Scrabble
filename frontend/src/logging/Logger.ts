type LoggerType = 
    "info" |
    "debug" |
    "error"

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
}


export default Logger;