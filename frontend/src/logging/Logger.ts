type LoggerType = 
    "info" |
    "debug" |
    "error"

class Logger {
    formatString: String = "";

    Logger(name: String) {
        this.formatString = `[${name}]`
    }    

    format(type: LoggerType) {
        return `${this.format} - [${type}] | `
    }

    debug(message: string) {
        console.log(this.format("debug") + message)
    }

    error(message: string) {
        console.log(this.format("error") + message)
    }
}


export default Logger;