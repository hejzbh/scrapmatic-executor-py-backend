from models.tasks.Task import Task

class PageToHtmlTask(Task):

    async def execute(self):
        try:
            await self.setStatus("RUNNING")

            html = self.inputs["webPage"]
            await self.setOutputs({"html":html, "webPage": html})

            await self.setStatus("COMPLETED")
            return self.outputs
        except Exception as e:
            await self.setStatus("FAILED")
            raise ValueError(e)